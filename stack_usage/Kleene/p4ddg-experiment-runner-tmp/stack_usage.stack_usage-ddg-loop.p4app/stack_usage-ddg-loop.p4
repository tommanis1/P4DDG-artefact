#include <core.p4>
#include <v1model.p4>

typedef bit<128> payload;

header payload_type {payload val;}
header num_t {bit<16> val;}
struct headers {
    num_t num;
    payload_type header_stack;
}

struct metadata {
    /* empty */
}

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {   
        bit<16> n;
        int<16> return_stack_index = 0;

state start {transition state_0;}

    state state_0 {
        packet.extract(hdr.num);
        transition state_9;    }

    state state_9 {
        n = hdr.num.val;        transition state_11;    }

    state state_11 {
        bit<10> tmp;
        if (n != 0){tmp = 0;}
        if (n == 0){tmp = 1;}
        transition select (tmp) {
            0 : state_19;
            1 : state_25;
        }
    }

    state state_19 {
        packet.extract(hdr.header_stack);
        transition state_21;    }

    state state_21 {
        n = n - 1;        transition state_23;    }

    state state_23 {
        bit<10> tmp;
        if (n != 0){tmp = 0;}
        if (n == 0){tmp = 1;}
        transition select (tmp) {
            0 : state_19;
            1 : state_25;
        }
    }

    state state_25 {
        transition accept;
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
