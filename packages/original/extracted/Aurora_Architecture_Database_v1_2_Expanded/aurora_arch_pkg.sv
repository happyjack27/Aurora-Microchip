package aurora_arch_pkg;

  typedef enum logic [2:0] {
    MODE_SCALAR32 = 3'd0,
    MODE_PACKED16 = 3'd1,
    MODE_PACKED8  = 3'd2,
    MODE_LOW16    = 3'd3,
    MODE_LOW8     = 3'd4,
    MODE_PAIRED64 = 3'd5
  } aurora_mode_e;

  typedef enum logic [3:0] {
    EXC_ILLEGAL_INSTRUCTION = 4'd0,
    EXC_ALIGNMENT_FAULT = 4'd1,
    EXC_ACCESS_FAULT = 4'd2,
    EXC_PRIVILEGE_FAULT = 4'd3,
    EXC_DIVIDE_BY_ZERO = 4'd4,
    EXC_SIGNED_DIV_OVERFLOW = 4'd5,
    EXC_BREAKPOINT = 4'd6,
    EXC_EXTERNAL_BUS_FAULT = 4'd7,
    EXC_RESERVED = 4'd15
  } aurora_exception_e;

  typedef struct packed {
    logic        valid;
    logic [31:0] pc;
    logic [7:0]  opcode;
    aurora_mode_e mode;
    logic [31:0] src_a;
    logic [31:0] src_b;
    logic [31:0] old_dst;
    logic [15:0] resource_mask;
    logic [2:0]  age;
  } issue_bundle_t;

  typedef struct packed {
    logic        valid;
    logic [2:0]  age;
    logic [31:0] pc;
    logic [31:0] dst_mask;
    logic [31:0] result_lo;
    logic [31:0] result_hi;
    aurora_exception_e fault_code;
    logic        store_commit;
    logic        complete;
  } completion_record_t;

endpackage