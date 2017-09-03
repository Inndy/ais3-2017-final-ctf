/*
 * NOTICE THAT YOU CAN NOT MODIFY THIS FILE, PYTHON LIB WILL PARSE THIS FILE!!
 *
 * You must add ',' to every line.
 * You muse add the comment at every line.
 *
 * Comment are composed in two parts: `T` and `C`
 *
 * `T` could be character list below
 *
 *     - I means I-type instruction
 *     - R means R-type instruction
 *
 * `C` means how many registers are used in this instruciton
 */

enum ZZOP {
    ZZOP_HLT    = 0x00, // R 0
    ZZOP_SYS    = 0x01, // R 0
    ZZOP_PUSI   = 0x02, // I 0
    ZZOP_ADDI   = 0x03, // I 2
    ZZOP_JGI    = 0x04, // I 2
    ZZOP_RET    = 0x05, // R 0
    ZZOP_ANDR   = 0x06, // R 3
    ZZOP_ANDI   = 0x07, // I 2
    ZZOP_CALL   = 0x08, // I 0
    ZZOP_ORI    = 0x09, // I 2
    ZZOP_SHRI   = 0x0a, // I 2
    ZZOP_XORI   = 0x0b, // I 2
    ZZOP_SHRR   = 0x0c, // R 3
    ZZOP_XORR   = 0x0d, // R 3
    ZZOP_JZI    = 0x0e, // I 1
    ZZOP_LD     = 0x0f, // I 2
    ZZOP_ST     = 0x10, // I 2
    ZZOP_NOP    = 0x11, // R 0
    ZZOP_MOVR   = 0x12, // R 2
    ZZOP_MOVI   = 0x13, // I 1
    ZZOP_POP    = 0x14, // R 1
    ZZOP_JNI    = 0x15, // I 2
    ZZOP_RAND   = 0x16, // R 0
    ZZOP_NOT    = 0x17, // R 0
    ZZOP_ORR    = 0x18, // R 3
    ZZOP_MULI   = 0x19, // I 2
    ZZOP_JEI    = 0x1a, // I 2
    ZZOP_PUSH   = 0x1b, // R 1
    ZZOP_ADDR   = 0x1c, // R 3
    ZZOP_NEG    = 0x1d, // R 2
    ZZOP_MULR   = 0x1e, // R 3
};
