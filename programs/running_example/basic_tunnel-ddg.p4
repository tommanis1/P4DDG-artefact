// SPDX-License-Identifier: Apache-2.0
/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_TUNNEL = 0x1212;
const bit<16> TYPE_IPV4 = 0x800;

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header myTunnel_t {
    bit<16> protoid;
    bit<16> dst_id;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

struct metadata_t {
    /* empty */
}

struct headers {
    ethernet_t   ethernet;
    myTunnel_t   tunnel;
    ipv4_t       ipv4;
}
// Place this header definition outside of your parser
header return_stack_type { bit<8> val;}
parser MyParser (packet_in packet,
    out headers hdr,
    inout metadata_t meta,
    inout standard_metadata_t standard_metadata) {

// Make these global variables of the parser
    bit<16> type;
return_stack_type[16] return_stack;
bit<8> return_stack_index = 0;
state start {
    transition state_0;
}
state state_0 {
    packet.extract(hdr.ethernet);
    transition state_6;
}
state state_1 {
    transition select (type == TYPE_IPV4,type == TYPE_TUNNEL) {
        (true, false) : state_14;
        (false, true) : state_24;
        default : state_10;
    }
}
state state_4 {
    transition accept;
}
state state_6 {
    type = hdr.ethernet.etherType;
    return_stack_index = return_stack_index + 1;
    return_stack[return_stack_index].val = 1;
    transition state_1;
}
state state_10 {
    transition accept;
}
state state_14 {
    packet.extract(hdr.ipv4);
    transition state_10;
}
state state_18 {
    transition state_10;
}
state state_24 {
    packet.extract(hdr.tunnel);
    transition state_26;
}
state state_26 {
    type = hdr.tunnel.protoid;
    return_stack_index = return_stack_index + 1;
    return_stack[return_stack_index].val = 2;
    transition state_1;
}
state state_continue {
    bit<8> tmp_return;
    if (return_stack_index == 0) { tmp_return = 0;} else {
        tmp_return = return_stack[return_stack_index].val;
        return_stack_index = return_stack_index - 1;
    }
    transition select (tmp_return) {
           1 : state_4;
           2 : state_18;
           0 : accept;
    }
}
}



/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata_t meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata_t meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
    }

    action myTunnel_forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
    }

    table myTunnel_exact {
        key = {
            hdr.tunnel.dst_id: exact;
        }
        actions = {
            myTunnel_forward;
            drop;
        }
        size = 1024;
        default_action = drop();
    }

    apply {
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata_t meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata_t meta) {
     apply {
        update_checksum(
            hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.tunnel);
        packet.emit(hdr.ipv4);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
