/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_MYTUNNEL = 0x1212; /* Ethernet type of the custmazied tunnel header */
const bit<16> TYPE_DETNET =0x9999; /* Ethernet type of detnet indication header */
const bit<16> TYPE_IPV4 = 0x800; /* Ethernet type of IPV4 packet */
const bit<16> DST_ID = 0x6; /*destination node setting */
const bit<16> STAG = 0x100; /* service layer tag: for now it is set constant bit but a service aware DetNet node must modify this value to gaureenty QoS requiremnt */
const bit<16> TTAG = 0x200; /* transport layer tag: for now it is set constant bit but a transport aware DetNet node must modify this value to gaureenty QoS requiremnt */
const bit<8>  UDP_PROTOCOL = 0x11;
const bit<5>  IPV4_OPTION_MRI = 31;

#define MAX_HOPS 9

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;
typedef bit<32> switchID_t;
typedef bit<32> qdepth_t;
typedef bit<16> myTunnelFields_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

/* Custamized detnet service indication header */
header detnetInd_t {
    bit<16> proto_id;
    bit<16> detnet_identifire;
}

/*Custamized tunnel header including destination ID, stag, and ttag */ 
header myTunnel_t {
    bit<16>	proto_id;
    myTunnelFields_t	dst_id;
    myTunnelFields_t    stag;
    myTunnelFields_t    ttag;
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

/* IPV4 option fields */
header ipv4_option_t {
    bit<1> copyFlag;
    bit<2> optClass;
    bit<5> option;
    bit<8> optionLength;
}

/* MRI header */
header mri_t {
    bit<16> count;
}

/* switch header indicating qdepth at switch/routers in the topology */
header switch_t {
    switchID_t swid;
    qdepth_t   qdepth;
}

struct ingress_metadata_t {
    bit<16> count;
}

struct parser_metadata_t {
    bit<16> remaining;
}

struct metadata_t {
    ingress_metadata_t ingress_metadata;
    parser_metadata_t  parser_metadata;
}

struct headers {
    ethernet_t         ethernet;
    detnetInd_t        detnetInd;
    myTunnel_t         myTunnel;
    ipv4_t             ipv4;
    ipv4_option_t      ipv4_option;
    mri_t              mri;
    switch_t[MAX_HOPS] swtraces;
}

error {IPHeaderTooShort}

// Place this header definition outside of your parser
header return_stack_type { bit<8> val;}
parser MyParser (packet_in packet,
    out headers hdr,
    inout metadata_t meta,
    inout standard_metadata_t standard_metadata) {

// Make these global variables of the parser
return_stack_type[16] return_stack;
bit<8> return_stack_index = 0;
state start {
    transition state_0;
}
state state_0 {
    packet.extract(hdr.ethernet);
    transition state_7;
}
state state_1 {
    packet.extract(hdr.ipv4);
    transition state_63;
}
state state_2 {
    packet.extract(hdr.swtraces.next);
    transition state_121;
}
state state_5 {
    transition state_continue;
}
state state_7 {
    transition select (hdr.ethernet.etherType  == TYPE_DETNET ,hdr.ethernet.etherType  == TYPE_MYTUNNEL ) {
        (true, false) : state_13;
        (false, true) : state_37;
        default : state_9;
    }
}
state state_9 {
    transition state_5;
}
state state_13 {
    packet.extract(hdr.detnetInd);
    transition state_17;
}
state state_17 {
    transition select (hdr.detnetInd.proto_id == TYPE_IPV4,hdr.detnetInd.proto_id == TYPE_IPV4) {
        (false, false) : state_19;
        (true, true) : state_23;
    }
}
state state_19 {
    transition state_5;
}
state state_23 {
    return_stack_index = return_stack_index + 1;
    return_stack[return_stack_index].val = 1;
    transition state_1;
}
state state_37 {
    packet.extract(hdr.myTunnel);
    transition state_41;
}
state state_41 {
    transition select (hdr.myTunnel.proto_id == TYPE_IPV4,hdr.myTunnel.proto_id == TYPE_IPV4) {
        (false, false) : state_43;
        (true, true) : state_47;
    }
}
state state_43 {
    transition state_9;
}
state state_47 {
    return_stack_index = return_stack_index + 1;
    return_stack[return_stack_index].val = 2;
    transition state_1;
}
state state_59 {
    transition state_continue;
}
state state_63 {
    verify(hdr.ipv4.ihl >= 5, error.IPHeaderTooShort);
    transition state_65;
}
state state_65 {
    transition select (hdr.ipv4.ihl == 5,hdr.ipv4.ihl == 5) {
        (true, true) : state_67;
        (false, false) : state_77;
    }
}
state state_67 {
    transition state_59;
}
state state_77 {
    packet.extract(hdr.ipv4_option);
    transition state_81;
}
state state_81 {
    transition select (hdr.ipv4_option.option == IPV4_OPTION_MRI,hdr.ipv4_option.option == IPV4_OPTION_MRI) {
        (false, false) : state_83;
        (true, true) : state_87;
    }
}
state state_83 {
    transition state_59;
}
state state_87 {
    packet.extract(hdr.mri);
    transition state_93;
}
state state_93 {
    meta.parser_metadata.remaining = hdr.mri.count;
    transition state_95;
}
state state_95 {
    transition select (meta.parser_metadata.remaining == 0,meta.parser_metadata.remaining == 0) {
        (true, true) : state_97;
        (false, false) : state_107;
    }
}
state state_97 {
    transition state_67;
}
state state_107 {
    return_stack_index = return_stack_index + 1;
    return_stack[return_stack_index].val = 3;
    transition state_2;
}
state state_117 {
    transition state_continue;
}
state state_121 {
    meta.parser_metadata.remaining = meta.parser_metadata.remaining - 1;
    transition state_123;
}
state state_123 {
    transition select (meta.parser_metadata.remaining == 0,meta.parser_metadata.remaining == 0) {
        (true, true) : state_125;
        (false, false) : state_135;
    }
}
state state_125 {
    transition state_117;
}
state state_135 {
    return_stack_index = return_stack_index + 1;
    return_stack[return_stack_index].val = 4;
    transition state_2;
}
state state_continue {
    bit<8> tmp_return;
    if (return_stack_index == 0) { tmp_return = 0;} else {
        tmp_return = return_stack[return_stack_index].val;
        return_stack_index = return_stack_index - 1;
    }
    transition select (tmp_return) {
           1 : state_19;
           2 : state_43;
           3 : state_97;
           4 : state_125;
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

    /* If the detnet indication header contains 1 this action should be applied  */ 
    action encap_act_detnetService1 (egressSpec_t port) {
	hdr.myTunnel.setValid();
	hdr.ethernet.etherType = TYPE_MYTUNNEL;
	hdr.myTunnel.proto_id = TYPE_IPV4;
        hdr.myTunnel.dst_id = DST_ID;
	hdr.myTunnel.stag = STAG;
	hdr.myTunnel.ttag = TTAG;
	hdr.detnetInd.setInvalid();
	standard_metadata.egress_spec = port;
    }

    /* If the detnet indication header contains 0 this action should be applied  */
    action encap_act_detnetService0 (egressSpec_t port) {
        hdr.detnetInd.setInvalid();
        hdr.myTunnel.setInvalid();
        hdr.ethernet.etherType = TYPE_IPV4;
        standard_metadata.egress_spec = port;
    }

    /* For normal IPV4 forwarding this action should be considered*/
    action ipv4_forward(macAddr_t dstAddr, egressSpec_t port) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = dstAddr;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
    }

	
    /* For tunnel forwarding this action need to be considered */ 
    action myTunnel_forward(egressSpec_t port) {
        standard_metadata.egress_spec = port;
    }

    /* decapsulation action at end switch/router */
    action decap_act(egressSpec_t port) {
        hdr.ethernet.etherType = TYPE_IPV4;
	hdr.myTunnel.setInvalid();
	hdr.detnetInd.setInvalid();
	standard_metadata.egress_spec = port;
    }

    /* drop action */
    action drop() {
        mark_to_drop(standard_metadata);
    }

    /* if detnet identifire bit is set to one apply this table */
    table encap_detnet_detnetService1 {
        key = {
            hdr.detnetInd.detnet_identifire: exact;
        }
	actions = {
	    encap_act_detnetService1;
	}
	size = 1024;
     }

    /* if detnet identifire bit is set to zero apply this table */
    table encap_detnet_detnetService0 {
        key = {
            hdr.detnetInd.detnet_identifire: exact;
        }
        actions = {
            encap_act_detnetService0;
        }
        size = 1024;
     }

     /*table for ipv4 forwarding */
     table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr : lpm;
        }
        actions = {
            ipv4_forward;
            drop;
            NoAction;
        }
        size = 1024;
        default_action = drop();
     }

    /*table for tunnel forwarding*/
    table myTunnel_exact {
        key = {
            hdr.myTunnel.dst_id : exact;
        }
        actions = {
            myTunnel_forward;
        }
        size = 1024;
    }

    /* table for removing myTunnel header at end switch/router */
    table decap_detnet {
        key = {
            hdr.myTunnel.dst_id : exact;
        }
        actions = {
            decap_act;
        }
        size = 1024;
    }
     
    /*Applying multiple match action*/
    apply {
        /* If only ipv4 is valid, do ipv forwarding */
        if (hdr.ipv4.isValid() && !hdr.myTunnel.isValid() && !hdr.detnetInd.isValid()) {
            ipv4_lpm.apply();
	}
	/* if detnet indication header is valid, detnet identifire bit is set to 1, and my tunnel header is not valid do tunneling */ 
	if (hdr.detnetInd.isValid() && hdr.detnetInd.detnet_identifire == 1 && !hdr.myTunnel.isValid()) {
                encap_detnet_detnetService1.apply();
        }
	/* if detnet indication header is valid, detnet identifire bit is set to 0, and my tunnel header is not valid do tunneling */
        if (hdr.detnetInd.isValid() && hdr.detnetInd.detnet_identifire == 0 && !hdr.myTunnel.isValid()) {
                encap_detnet_detnetService0.apply();
        }
	/* if myTunnel is valid just forward packets using myTunnel header */
        if (hdr.myTunnel.isValid()){
		myTunnel_exact.apply();
		decap_detnet.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata_t meta,
                 inout standard_metadata_t standard_metadata) {
    action add_swtrace(switchID_t swid) {
        hdr.mri.count = hdr.mri.count + 1;
        hdr.swtraces.push_front(1);
        hdr.swtraces[0].setValid();
        hdr.swtraces[0].swid = swid;
        hdr.swtraces[0].qdepth = (qdepth_t)standard_metadata.deq_qdepth;
        hdr.ipv4.ihl = hdr.ipv4.ihl + 2;
        hdr.ipv4_option.optionLength = hdr.ipv4_option.optionLength + 8;
        hdr.ipv4.totalLen = hdr.ipv4.totalLen + 8;
    }

    table swtrace {
        actions = {
            add_swtrace;
            NoAction;
        }
        default_action = NoAction();
    }

    apply {
        if (hdr.mri.isValid()) {
	    swtrace.apply();
	}
    }
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
	packet.emit(hdr.detnetInd);
	packet.emit(hdr.myTunnel);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ipv4_option);
        packet.emit(hdr.mri);
        packet.emit(hdr.swtraces);
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
