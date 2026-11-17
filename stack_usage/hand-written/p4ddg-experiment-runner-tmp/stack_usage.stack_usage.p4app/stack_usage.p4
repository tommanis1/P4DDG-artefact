#include <core.p4>
#include <v1model.p4>

typedef bit<128> payload;

header payload_type {payload val;}
header num_t {bit<16> val;}
struct headers {
    num_t num;
    payload_type[50] header_stack;
}

struct metadata {
    /* empty */
}

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {   
    bit<16> todo = 0;
    state start {transition parse_num;}

    state parse_num  {
        packet.extract(hdr.num);
        todo = hdr.num.val;
        transition check;
    }

    state check {
        transition select(todo) {
            0 : accept;
            default: extract;
        }
    }

    state extract {
        packet.extract(hdr.header_stack.next);
        todo = todo -1 ;

        transition check;
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
