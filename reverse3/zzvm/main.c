#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "zzvm.h"

#define ZZ_IMAGE_MAGIC   ('O' | ('o' << 8))/* 'Oo' */
#define ZZ_IMAGE_VERSION 0x0

typedef struct __attribute__((__packed__)) {
    ZZ_ADDRESS section_addr;
    ZZ_ADDRESS section_size;
} ZZ_SECTION_HEADER;

typedef struct __attribute__((__packed__)) {
    uint16_t          magic;
    uint16_t          file_ver;
    ZZ_ADDRESS        entry;
    uint16_t          section_count;
    ZZ_SECTION_HEADER sections[0];
} ZZ_IMAGE_HEADER;

// decode a byte of Zz-encoded data (encoded) to buffer (out)
int zz_decode_byte(const char *encoded, uint8_t *out)
{
    uint8_t value = 0;

    for(int i = 0; i < 8; i++)
    {
        value <<= 1;
        if(encoded[i] == 'O') {
            value |= 1;
        } else if(encoded[i] != 'o') {
            return 0;
        }
    }

    *out = value;
    return 1;
}

// decode Zz-encoded data from source (src) to buffer (dst)
int zz_decode_data(void *dst, const void *src, size_t unpacked_size)
{
    uint8_t *dst8 = (uint8_t *)dst;
    uint64_t i, val, packed_size;

    for(i = 0; i < unpacked_size; i++) {
        if(!zz_decode_byte(src + i * 8, &dst8[i])) {
            return 0;
        }
    }

    return 1;
}

// read and decode header data from file (fp) to buffer (header)
int zz_read_image_header(FILE *fp, ZZ_IMAGE_HEADER *header)
{
    char buffer[sizeof(*header) * 8];

    if(fread(buffer, sizeof(buffer), 1, fp) != 1) {
        fprintf(stderr, "Unable to read file\n");
        return 0;
    }

    if(!zz_decode_data(header, buffer, sizeof(*header))) {
        fprintf(stderr, "Malformed file\n");
        return 0;
    }

    return 1;
}

// verify header data (header), checking magic number and file version
int zz_verify_image_header(ZZ_IMAGE_HEADER *header)
{
    if(header->magic != ZZ_IMAGE_MAGIC) {
        fprintf(stderr, "Invalid file magic (%.4x)\n", header->magic);
        return 0;
    }

    if(header->file_ver != ZZ_IMAGE_VERSION) {
        fprintf(stderr, "Mismatch file version\n");
        return 0;
    }

    return 1;
}

// read and decode header->sections
int zz_read_image_header_section(FILE *fp, ZZ_SECTION_HEADER *section)
{
    char buffer[sizeof(*section) * 8];

    if(fread(buffer, sizeof(buffer), 1, fp) != 1) {
        fprintf(stderr, "Can not read file section\n");
        return 0;
    }

    if(!zz_decode_data(section, buffer, sizeof(*section))) {
        fprintf(stderr, "Malformed file\n");
        return 0;
    }

    return 1;
}

// read and decode ZZ_IMAGE_HEADER
int zz_load_image_header(FILE *fp, ZZ_IMAGE_HEADER **out_header)
{
    ZZ_IMAGE_HEADER *header = (ZZ_IMAGE_HEADER *)malloc(sizeof(ZZ_IMAGE_HEADER));

    if(!zz_read_image_header(fp, header)) {
        return 0;
    }
    if(!zz_verify_image_header(header)) {
        return 0;
    }

    header = (ZZ_IMAGE_HEADER *)realloc(header, sizeof(ZZ_IMAGE_HEADER) +
            sizeof(ZZ_SECTION_HEADER) * header->section_count);

    for(int i = 0; i < header->section_count; i++) {
        if(!zz_read_image_header_section(fp, &header->sections[i])) {
            return 0;
        }
    }

    *out_header = header;
    return 1;
}

// read, decode image and put things into an existed vm
int zz_load_image_to_vm(const char *filename, ZZVM *vm, ZZ_IMAGE_HEADER **out_header)
{
    FILE *fp;
    ZZ_IMAGE_HEADER *header = NULL;

    if(strcmp(filename, "-") == 0 || filename == NULL) {
        fp = stdin;
    } else {
        fp = fopen(filename, "rb");
    }

    if(!fp) {
        fprintf(stderr, "Unable to open file\n");
        return 0;
    }

    if(!zz_load_image_header(fp, &header)) {
        return 0;
    }

    vm->ctx.regs.IP = header->entry;

    size_t buffer_size = 8192;
    char *buffer = malloc(buffer_size);

    for(int i = 0; i < header->section_count; i++) {
        ZZ_SECTION_HEADER *section_header = &header->sections[i];

        size_t size_bound = (size_t)section_header->section_addr +
                            (size_t)section_header->section_size;
        size_t encoded_size = section_header->section_size * 8;

        if(size_bound >= sizeof(vm->ctx.memory)) {
            fprintf(stderr, "Section#%d out of scope\n", i);
            goto fail;
        }

        if(buffer_size < encoded_size) {
            buffer_size = encoded_size;
            buffer = realloc(buffer, buffer_size);
        }

        if(fread(buffer, encoded_size, 1, fp) != 1) {
            fprintf(stderr, "Can not read section #%d\n", i);
            goto fail;
        }

        if(!zz_decode_data(&vm->ctx.memory[section_header->section_addr], buffer, section_header->section_size)) {
            fprintf(stderr, "Malformed file\n");
            goto fail;
        }
    }

    if(fp != stdin) fclose(fp);
    if(out_header) {
        *out_header = header;
    } else {
        free(header);
    }
    free(buffer);

    return 1;

fail:
    if(fp && fp != stdin) fclose(fp);
    if(header) free(header);
    if(buffer) free(buffer);
    return 0;
}

// load zz-image into vm and run
int run_file(const char *filename, int trace)
{
    ZZVM *vm;
    if(zz_create(&vm) != ZZ_SUCCESS) {
        fprintf(stderr, "Can not create vm\n");
        return 0;
    }

    if(!zz_load_image_to_vm(filename, vm, NULL)) {
        return 0;
    }

    zz_msg_pipe = stderr;

    int stop_reason = ZZ_SUCCESS;
    while(1) {
        if(trace) {
            char buffer[64];
            ZZ_INSTRUCTION *ins = zz_fetch(&vm->ctx);
            zz_disasm(vm->ctx.regs.IP, ins, buffer, sizeof(buffer) - 1);
            fprintf(zz_msg_pipe, "[TRACE] %.4x: %s\n", vm->ctx.regs.IP, buffer);
        }

        if(stop_reason == ZZ_HALT) {
            break;
        }

        if(zz_execute(vm, 1, &stop_reason) != ZZ_SUCCESS) {
            fprintf(zz_msg_pipe, "Failed to execute, IP = %.4x, stop_reason = %d\n",
                    vm->ctx.regs.IP, stop_reason);
            break;
        }
    }

    zz_destroy(vm);
    return 1;
}

int main(int argc, const char * const argv[])
{
    if(argc < 2) {
        printf("Usage: %s vm-image\n", argv[0]);
        return 1;
    }
    run_file(argv[1], 0);
}
