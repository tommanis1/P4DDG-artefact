#include <core.p4>
#include <v1model.p4>

typedef bit<128> payload;

header payload_type {payload val;}
header num_t {int<16> val;}
struct headers {
    num_t num;
    payload_type header_stack;
}

struct metadata {
    /* empty */
}
header return_stack_type { int<16> val;}


parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {   
        return_stack_type[100] return_stack;
        int<16> return_stack_index = 0;
        int<16> n;
        state start {transition state_0;}

    state state_0 {
        packet.extract(hdr.num);
        transition state_6;    }

    state state_1 {
        bit<10> tmp;
        if (n == 0){tmp = 0;}
        if (n != 0){tmp = 1;}
        transition select (tmp) {
            0 : state_12;
            1 : state_18;
        }
    }

    state state_6 {
        return_stack_index = return_stack_index + 1;
        return_stack[return_stack_index].val = 1;
        n = hdr.num.val;
        transition state_1;    }

    state state_8 {
        // accepting state
        int<16> tmp_return;
        if (return_stack_index == 0) { tmp_return = 0;} else {
            tmp_return = return_stack[return_stack_index].val;return_stack_index = return_stack_index - 1;}
        transition select (tmp_return) {
        0 : accept;
            1 : state_8;
            2 : state_22;
        }
    }

    state state_12 {
        // accepting state
        int<16> tmp_return;
        if (return_stack_index == 0) { tmp_return = 0;} else {
            tmp_return = return_stack[return_stack_index].val;return_stack_index = return_stack_index - 1;}
        transition select (tmp_return) {
        0 : accept;
            1 : state_8;
            2 : state_22;
        }
    }

    state state_18 {
        packet.extract(hdr.header_stack);        
        transition state_20;    
        }

    state state_20 {
        return_stack_index = return_stack_index + 1;
        return_stack[return_stack_index].val = 1;
        n = n-1;
        transition state_1;    }

    state state_22 {
        // accepting state
        int<16> tmp_return;
        if (return_stack_index == 0) { tmp_return = 0;} else {
            tmp_return = return_stack[return_stack_index].val;return_stack_index = return_stack_index - 1;}
        transition select (tmp_return) {
        0 : accept;
            1 : state_8;
            2 : state_22;
        }
    }



}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {    apply {  }
                  }
control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {}}

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
    }
}

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
