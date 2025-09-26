# Based on GPU_VIPER.py edited by Victor Fritz Trost (c) 2025 edits under the MIT license

# Copyright (c) 2011-2015 Advanced Micro Devices, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import math

from common import (
    FileSystemConfig,
    MemConfig,
    ObjectList,
)

import m5
from m5.defines import buildEnv
from m5.objects import *
from m5.util import addToPath

from .Ruby import (
    create_topology,
    send_evicts,
)

addToPath("../")

from topologies.Cluster import Cluster
from topologies.Crossbar import Crossbar


class CntrlBase:
    _seqs = 0

    @classmethod
    def seqCount(cls):
        # Use SeqCount not class since we need global count
        CntrlBase._seqs += 1
        return CntrlBase._seqs - 1

    _cntrls = 0

    @classmethod
    def cntrlCount(cls):
        # Use CntlCount not class since we need global count
        CntrlBase._cntrls += 1
        return CntrlBase._cntrls - 1

    _version = 0

    @classmethod
    def versionCount(cls):
        cls._version += 1  # Use count for this particular type
        return cls._version - 1

class L1Cache(GPU_VIPER_CXL_MESIF_L1Cache_Controller):
    _version = 0

    @classmethod
    def versionCount(cls):
        cls._version += 1  # Use count for this particular type
        return cls._version - 1

    def dcache(self):
        return self.cache


    def __init__(self, system, ruby_system, cpu, cluster_id, options):
        """CPUs are needed to grab the clock domain and system is needed for
        the cache block size.
        """
        super().__init__()

        self.version = self.versionCount()
        self.cache = RubyCache(
            size=options.l1d_size, assoc=options.l1d_assoc, start_index_bit=self.getBlockSizeBits(system), is_icache=False
        )
        
        self.l2_id = cluster_id
        if cpu:
            self.clk_domain = cpu.clk_domain # TODO: FIXME

        self.send_evictions = self.sendEvicts(cpu)
        self.ruby_system = ruby_system
        # self.enable_prefetch = False
        # self.prefetcher = RubyPrefetcher()
        self.connectQueues(ruby_system)

    def getBlockSizeBits(self, system):
        bits = int(math.log(system.cache_line_size, 2))
        if 2**bits != system.cache_line_size.value:
            panic("Cache line size not a power of 2!")
        return bits

    def sendEvicts(self, cpu):
        """True if the CPU model or ISA requires sending evictions from caches
        to the CPU. Two scenarios warrant forwarding evictions to the CPU:
        1. The O3 model must keep the LSQ coherent with the caches
        2. The x86 mwait instruction is built on top of coherence
        3. The local exclusive monitor in ARM systems

        As this is an X86 simulation we return True.
        """
        return True

    def connectQueues(self, ruby_system):
        """Connect all of the queues for this controller."""
        self.mandatoryQueue = MessageBuffer()


        self.fwdTo = MessageBuffer(ordered=True)
        self.fwdTo.in_port = ruby_system.network.out_port

        self.fwdFrom = MessageBuffer(ordered=True)
        self.fwdFrom.out_port = ruby_system.network.in_port

        self.respTo = MessageBuffer(ordered=True)
        self.respTo.in_port = ruby_system.network.out_port

        self.respFrom = MessageBuffer(ordered=True)
        self.respFrom.out_port = ruby_system.network.in_port

        self.reqTo = MessageBuffer(ordered=True)
        self.reqTo.in_port = ruby_system.network.out_port

        self.reqFrom = MessageBuffer(ordered=True)
        self.reqFrom.out_port = ruby_system.network.in_port

class L0Cache(GPU_VIPER_CXL_MESIF_L0Cache_Controller):
    _version = 0

    @classmethod
    def versionCount(cls):
        cls._version += 1  # Use count for this particular type
        return cls._version - 1

    def __init__(self, system, ruby_system, options):
        """CPUs are needed to grab the clock domain and system is needed for
        the cache block size.
        """
        super().__init__()

        self.version = self.versionCount()
        # This is the cache memory object that stores the cache data and tags
        self.cache = RubyCache(
            size=options.l2_size, assoc=options.l2_assoc, start_index_bit=self.getBlockSizeBits(system), is_icache=False
        )
        self.ruby_system = ruby_system
        self.connectQueues(ruby_system)

    def getBlockSizeBits(self, system):
        bits = int(math.log(system.cache_line_size, 2))
        if 2**bits != system.cache_line_size.value:
            panic("Cache line size not a power of 2!")
        return bits

    def connectQueues(self, ruby_system):
        """Connect all of the queues for this controller."""

        self.bisnpTo = MessageBuffer(ordered=True)
        self.bisnpTo.in_port = ruby_system.network.out_port
        self.bisnpFrom = MessageBuffer(ordered=True)
        self.bisnpFrom.out_port = ruby_system.network.in_port
        self.birspTo = MessageBuffer(ordered=True)
        self.birspTo.in_port = ruby_system.network.out_port
        self.birspFrom = MessageBuffer(ordered=True)
        self.birspFrom.out_port = ruby_system.network.in_port


        self.ndrTo = MessageBuffer(ordered=True)
        self.ndrTo.in_port = ruby_system.network.out_port
        self.ndrFrom = MessageBuffer(ordered=True)
        self.ndrFrom.out_port = ruby_system.network.in_port
        self.drsTo = MessageBuffer(ordered=True)
        self.drsTo.in_port = ruby_system.network.out_port
        self.drsFrom = MessageBuffer(ordered=True)
        self.drsFrom.out_port = ruby_system.network.in_port

        self.req2To = MessageBuffer(ordered=True)
        self.req2To.in_port = ruby_system.network.out_port
        self.req2From = MessageBuffer(ordered=True)
        self.req2From.out_port = ruby_system.network.in_port
        self.rwdTo = MessageBuffer(ordered=True)
        self.rwdTo.in_port = ruby_system.network.out_port
        self.rwdFrom = MessageBuffer(ordered=True)
        self.rwdFrom.out_port = ruby_system.network.in_port

        self.fwdTo = MessageBuffer(ordered=True)
        self.fwdTo.in_port = ruby_system.network.out_port

        self.fwdFrom = MessageBuffer(ordered=True)
        self.fwdFrom.out_port = ruby_system.network.in_port

        self.respTo = MessageBuffer(ordered=True)
        self.respTo.in_port = ruby_system.network.out_port

        self.respFrom = MessageBuffer(ordered=True)
        self.respFrom.out_port = ruby_system.network.in_port

        self.reqTo = MessageBuffer(ordered=True)
        self.reqTo.in_port = ruby_system.network.out_port

        self.reqFrom = MessageBuffer(ordered=True)
        self.reqFrom.out_port = ruby_system.network.in_port

class DirController(GPU_VIPER_CXL_MESIF_Directory_Controller):
    _version = 0

    @classmethod
    def versionCount(cls):
        cls._version += 1  # Use count for this particular type
        return cls._version - 1

    def __init__(self, ruby_system, ranges, mem_ctrl):
        """ranges are the memory ranges assigned to this controller."""
        super().__init__()
        self.version = self.versionCount()
        self.addr_ranges = ranges
        self.ruby_system = ruby_system
        self.directory = RubyDirectoryMemory()
        # Connect this directory to the memory side.
        #self.memory = mem_ctrls[0].port
        #self.memory_out_port = mem_ctrl.port
        self.directory.block_size = ruby_system.block_size_bytes
        self.connectQueues(ruby_system)

    def connectQueues(self, ruby_system):
        self.requestToMemory = MessageBuffer()
        self.responseFromMemory = MessageBuffer()

        self.fwdTo = MessageBuffer(ordered=True)
        self.fwdTo.in_port = ruby_system.network.out_port

        self.fwdFrom = MessageBuffer(ordered=True)
        self.fwdFrom.out_port = ruby_system.network.in_port

        self.respTo = MessageBuffer(ordered=True)
        self.respTo.in_port = ruby_system.network.out_port

        self.respFrom = MessageBuffer(ordered=True)
        self.respFrom.out_port = ruby_system.network.in_port

        self.reqTo = MessageBuffer(ordered=True)
        self.reqTo.in_port = ruby_system.network.out_port

        self.reqFrom = MessageBuffer(ordered=True)
        self.reqFrom.out_port = ruby_system.network.in_port

        self.bisnpTo = MessageBuffer(ordered=True)
        self.bisnpTo.in_port = ruby_system.network.out_port
        self.bisnpFrom = MessageBuffer(ordered=True)
        self.bisnpFrom.out_port = ruby_system.network.in_port
        self.birspTo = MessageBuffer(ordered=True)
        self.birspTo.in_port = ruby_system.network.out_port
        self.birspFrom = MessageBuffer(ordered=True)
        self.birspFrom.out_port = ruby_system.network.in_port


        self.ndrTo = MessageBuffer(ordered=True)
        self.ndrTo.in_port = ruby_system.network.out_port
        self.ndrFrom = MessageBuffer(ordered=True)
        self.ndrFrom.out_port = ruby_system.network.in_port
        self.drsTo = MessageBuffer(ordered=True)
        self.drsTo.in_port = ruby_system.network.out_port
        self.drsFrom = MessageBuffer(ordered=True)
        self.drsFrom.out_port = ruby_system.network.in_port

        self.req2To = MessageBuffer(ordered=True)
        self.req2To.in_port = ruby_system.network.out_port
        self.req2From = MessageBuffer(ordered=True)
        self.req2From.out_port = ruby_system.network.in_port
        self.rwdTo = MessageBuffer(ordered=True)
        self.rwdTo.in_port = ruby_system.network.out_port
        self.rwdFrom = MessageBuffer(ordered=True)
        self.rwdFrom.out_port = ruby_system.network.in_port

class TCPCache(RubyCache):
    size = "16KiB"
    assoc = 16
    dataArrayBanks = 16  # number of data banks
    tagArrayBanks = 16  # number of tag banks
    dataAccessLatency = 4
    tagAccessLatency = 1

    def create(self, options):
        self.size = MemorySize(options.tcp_size)
        self.assoc = options.tcp_assoc
        self.resourceStalls = options.no_tcc_resource_stalls
        if hasattr(options, "tcp_rp"):
            self.replacement_policy = ObjectList.rp_list.get(options.tcp_rp)()


class TCPCntrl(GPU_VIPER_CXL_MESIF_TCP_Controller, CntrlBase):
    def create(self, options, ruby_system, system):
        self.version = self.versionCount()

        self.L1cache = TCPCache(
            tagAccessLatency=options.TCP_latency,
            dataAccessLatency=options.TCP_latency,
        )
        self.L1cache.resourceStalls = options.no_resource_stalls
        self.L1cache.dataArrayBanks = options.tcp_num_banks
        self.L1cache.tagArrayBanks = options.tcp_num_banks
        self.L1cache.create(options)
        self.issue_latency = 1
        # TCP_Controller inherits this from RubyController
        self.mandatory_queue_latency = options.mandatory_queue_latency

        self.coalescer = VIPERCoalescer(ruby_system=ruby_system)
        self.coalescer.version = self.seqCount()
        self.coalescer.icache = self.L1cache
        self.coalescer.dcache = self.L1cache
        self.coalescer.ruby_system = ruby_system
        self.coalescer.support_inst_reqs = False
        self.coalescer.is_cpu_sequencer = False
        if options.tcp_deadlock_threshold:
            self.coalescer.deadlock_threshold = options.tcp_deadlock_threshold
        self.coalescer.max_coalesces_per_cycle = (
            options.max_coalesces_per_cycle
        )

        self.sequencer = RubySequencer(ruby_system=ruby_system)
        self.sequencer.version = self.seqCount()
        self.sequencer.dcache = self.L1cache
        self.sequencer.ruby_system = ruby_system
        self.sequencer.is_cpu_sequencer = True

        self.use_seq_not_coal = False

        self.ruby_system = ruby_system
        if hasattr(options, "gpu_clock") and hasattr(options, "gpu_voltage"):
            self.clk_domain = SrcClockDomain(
                clock=options.gpu_clock,
                voltage_domain=VoltageDomain(voltage=options.gpu_voltage),
            )

        if options.recycle_latency:
            self.recycle_latency = options.recycle_latency

    def createCP(self, options, ruby_system, system):
        self.version = self.versionCount()

        self.L1cache = TCPCache(
            tagAccessLatency=options.TCP_latency,
            dataAccessLatency=options.TCP_latency,
        )
        self.L1cache.resourceStalls = options.no_resource_stalls
        self.L1cache.create(options)
        self.issue_latency = 1

        self.coalescer = VIPERCoalescer(ruby_system=ruby_system)
        self.coalescer.version = self.seqCount()
        self.coalescer.icache = self.L1cache
        self.coalescer.dcache = self.L1cache
        self.coalescer.ruby_system = ruby_system
        self.coalescer.support_inst_reqs = False
        self.coalescer.is_cpu_sequencer = False

        self.sequencer = RubySequencer(ruby_system=ruby_system)
        self.sequencer.version = self.seqCount()
        self.sequencer.dcache = self.L1cache
        self.sequencer.ruby_system = ruby_system
        self.sequencer.is_cpu_sequencer = True

        self.use_seq_not_coal = True

        self.ruby_system = ruby_system

        if options.recycle_latency:
            self.recycle_latency = options.recycle_latency


class SQCCache(RubyCache):
    dataArrayBanks = 8
    tagArrayBanks = 8
    dataAccessLatency = 1
    tagAccessLatency = 1

    def create(self, options):
        self.size = MemorySize(options.sqc_size)
        self.assoc = options.sqc_assoc
        if hasattr(options, "sqc_rp"):
            self.replacement_policy = ObjectList.rp_list.get(options.sqc_rp)()


class SQCCntrl(GPU_VIPER_CXL_MESIF_SQC_Controller, CntrlBase):
    def create(self, options, ruby_system, system):
        self.version = self.versionCount()

        self.L1cache = SQCCache()
        self.L1cache.create(options)
        self.L1cache.resourceStalls = options.no_resource_stalls

        self.sequencer = VIPERSequencer()

        self.sequencer.version = self.seqCount()
        self.sequencer.dcache = self.L1cache
        self.sequencer.ruby_system = ruby_system
        self.sequencer.support_data_reqs = False
        self.sequencer.is_cpu_sequencer = False
        if options.sqc_deadlock_threshold:
            self.sequencer.deadlock_threshold = options.sqc_deadlock_threshold

        self.ruby_system = ruby_system
        if hasattr(options, "gpu_clock") and hasattr(options, "gpu_voltage"):
            self.clk_domain = SrcClockDomain(
                clock=options.gpu_clock,
                voltage_domain=VoltageDomain(voltage=options.gpu_voltage),
            )

        if options.recycle_latency:
            self.recycle_latency = options.recycle_latency


class TCC(RubyCache):
    size = MemorySize("256KiB")
    assoc = 16
    dataAccessLatency = 8
    tagAccessLatency = 2
    resourceStalls = True

    def create(self, options):
        self.assoc = options.tcc_assoc
        self.atomicLatency = options.atomic_alu_latency
        self.atomicALUs = options.tcc_num_atomic_alus
        if hasattr(options, "bw_scalor") and options.bw_scalor > 0:
            s = options.num_compute_units
            tcc_size = s * 128
            tcc_size = str(tcc_size) + "KiB"
            self.size = MemorySize(tcc_size)
            self.dataArrayBanks = 64
            self.tagArrayBanks = 64
        else:
            self.size = MemorySize(options.tcc_size)
            self.dataArrayBanks = (
                256 / options.num_tccs
            )  # number of data banks
            self.tagArrayBanks = 256 / options.num_tccs  # number of tag banks
        self.size.value = self.size.value / options.num_tccs
        if (self.size.value / int(self.assoc)) < 128:
            self.size.value = int(128 * self.assoc)
        self.start_index_bit = math.log(options.cacheline_size, 2) + math.log(
            options.num_tccs, 2
        )
        if hasattr(options, "tcc_rp"):
            self.replacement_policy = ObjectList.rp_list.get(options.tcc_rp)()


class TCCCntrl(GPU_VIPER_CXL_MESIF_TCC_Controller, CntrlBase):
    def create(self, options, ruby_system, system):
        self.version = self.versionCount()
        self.L2cache = TCC(
            tagAccessLatency=options.tcc_tag_access_latency,
            dataAccessLatency=options.tcc_data_access_latency,
        )
        self.L2cache.create(options)
        self.L2cache.resourceStalls = options.no_tcc_resource_stalls

        self.ruby_system = ruby_system
        if hasattr(options, "gpu_clock") and hasattr(options, "gpu_voltage"):
            self.clk_domain = SrcClockDomain(
                clock=options.gpu_clock,
                voltage_domain=VoltageDomain(voltage=options.gpu_voltage),
            )

        if options.recycle_latency:
            self.recycle_latency = options.recycle_latency

    def connect_cxl(self, ruby_system): 
        
        self.bisnpTo = MessageBuffer(ordered=True)
        self.bisnpTo.in_port = ruby_system.network.out_port
        self.bisnpFrom = MessageBuffer(ordered=True)
        self.bisnpFrom.out_port = ruby_system.network.in_port
        self.birspTo = MessageBuffer(ordered=True)
        self.birspTo.in_port = ruby_system.network.out_port
        self.birspFrom = MessageBuffer(ordered=True)
        self.birspFrom.out_port = ruby_system.network.in_port


        self.ndrTo = MessageBuffer(ordered=True)
        self.ndrTo.in_port = ruby_system.network.out_port
        self.ndrFrom = MessageBuffer(ordered=True)
        self.ndrFrom.out_port = ruby_system.network.in_port
        self.drsTo = MessageBuffer(ordered=True)
        self.drsTo.in_port = ruby_system.network.out_port
        self.drsFrom = MessageBuffer(ordered=True)
        self.drsFrom.out_port = ruby_system.network.in_port

        self.req2To = MessageBuffer(ordered=True)
        self.req2To.in_port = ruby_system.network.out_port
        self.req2From = MessageBuffer(ordered=True)
        self.req2From.out_port = ruby_system.network.in_port
        self.rwdTo = MessageBuffer(ordered=True)
        self.rwdTo.in_port = ruby_system.network.out_port
        self.rwdFrom = MessageBuffer(ordered=True)
        self.rwdFrom.out_port = ruby_system.network.in_port


def define_options(parser):
    parser.add_argument("--to-dir-latency", type=int, default=140, help="latency from l2/tcc to the directory ^= CXL latency")


    parser.add_argument(
        "--no-resource-stalls", action="store_false", default=True
    )

    parser.add_argument(
        "--no-tcc-resource-stalls", action="store_false", default=True
    )

    parser.add_argument(
        "--num-tccs",
        type=int,
        default=1,
        help="number of TCC banks in the GPU",
    )
    parser.add_argument(
        "--sqc-size", type=str, default="32KiB", help="SQC cache size"
    )
    parser.add_argument(
        "--sqc-assoc", type=int, default=8, help="SQC cache assoc"
    )
    parser.add_argument(
        "--sqc-deadlock-threshold",
        type=int,
        help="Set the SQC deadlock threshold to some value",
    )

    parser.add_argument(
        "--WB_L1", action="store_true", default=False, help="writeback L1"
    )

    parser.add_argument(
        "--TCP_latency",
        type=int,
        default=4,
        help="In combination with the number of banks for the "
        "TCP, this determines how many requests can happen "
        "per cycle (i.e., the bandwidth)",
    )
    parser.add_argument(
        "--mandatory_queue_latency",
        type=int,
        default=1,
        help="Hit latency for TCP",
    )
    parser.add_argument(
        "--TCC_latency", type=int, default=16, help="TCC latency"
    )
    parser.add_argument(
        "--tcc-size", type=str, default="256KiB", help="agregate tcc size"
    )
    parser.add_argument("--tcc-assoc", type=int, default=16, help="tcc assoc")
    parser.add_argument(
        "--tcp-size", type=str, default="16KiB", help="tcp size"
    )
    parser.add_argument("--tcp-assoc", type=int, default=16, help="tcp assoc")
    parser.add_argument(
        "--tcp-deadlock-threshold",
        type=int,
        help="Set the TCP deadlock threshold to some value",
    )
    parser.add_argument(
        "--max-coalesces-per-cycle",
        type=int,
        default=1,
        help="Maximum insts that may coalesce in a cycle",
    )

    parser.add_argument(
        "--noL1", action="store_true", default=False, help="bypassL1"
    )
    parser.add_argument(
        "--glc-atomic-latency", type=int, default=1, help="GLC Atomic Latency"
    )
    parser.add_argument(
        "--atomic-alu-latency", type=int, default=0, help="Atomic ALU Latency"
    )
    parser.add_argument(
        "--tcc-num-atomic-alus",
        type=int,
        default=64,
        help="Number of atomic ALUs in the TCC",
    )
    parser.add_argument(
        "--tcp-num-banks",
        type=int,
        default="16",
        help="Num of banks in L1 cache",
    )
    parser.add_argument(
        "--tcc-tag-access-latency",
        type=int,
        default="2",
        help="Tag access latency in L2 cache",
    )
    parser.add_argument(
        "--tcc-data-access-latency",
        type=int,
        default="8",
        help="Data access latency in L2 cache",
    )


def construct_dirs(options, system, ruby_system, network):
    dir_cntrl_nodes = []
    mem_ctrl = MemCtrl()
    mem_ctrl.dram = DDR3_1600_8x8()
    mem_ctrl.dram.range = system.mem_ranges[0]

    # For an odd number of CPUs, still create the right number of controllers
    TCC_bits = int(math.log(options.num_tccs, 2))

    if options.numa_high_bit:
        numa_bit = options.numa_high_bit
    else:
        # if the numa_bit is not specified, set the directory bits as the
        # lowest bits above the block offset bits, and the numa_bit as the
        # highest of those directory bits
        dir_bits = int(math.log(options.num_dirs, 2))
        block_size_bits = int(math.log(options.cacheline_size, 2))
        numa_bit = block_size_bits + dir_bits - 1

    for i in range(options.num_dirs):
        dir_ranges = []
        for r in system.mem_ranges:
            addr_range = m5.objects.AddrRange(
                r.start,
                size=r.size(),
                intlvHighBit=numa_bit,
                intlvBits=dir_bits,
                intlvMatch=i,
            )
            dir_ranges.append(addr_range)

        dir_cntrl = DirController(ruby_system, dir_ranges, mem_ctrl)

        dir_cntrl.requestFromDMA = MessageBuffer(ordered=True)
        dir_cntrl.requestFromDMA.in_port = network.out_port

        dir_cntrl.responseToDMA = MessageBuffer()
        dir_cntrl.responseToDMA.out_port = network.in_port

        exec("ruby_system.dir_cntrl%d = dir_cntrl" % i)
        dir_cntrl_nodes.append(dir_cntrl)

    return dir_cntrl_nodes

def construct_l1s(options, system, ruby_system, network):
    l1_sequencers = []
    l1_cntrl_nodes = []

    # For an odd number of CPUs, still create the right number of controllers
    TCC_bits = int(math.log(options.num_tccs, 2))

    for i in range(options.num_cpus):
        l1 = L1Cache(system, ruby_system, None, 0, options)
        exec("ruby_system.l1_cntrl%d = l1" % i)
        l1_cntrl_nodes.append(l1)
        sequencer = RubySequencer(ruby_system=ruby_system)
        sequencer.version = i;
        sequencer.dcache = l1.dcache()
        sequencer.ruby_system = ruby_system
        sequencer.coreid = i
        sequencer.is_cpu_sequencer = True
        l1.sequencer = sequencer

        l1_sequencers.append(sequencer)
    
    return (l1_sequencers, l1_cntrl_nodes)
    
def construct_l2(system, ruby_system, cluster, options):
    l2 = L0Cache(system, ruby_system, options)
    exec("ruby_system.l2_cntrl%d = l2" % cluster)
    return l2   


def construct_tcps(options, system, ruby_system, network):
    tcp_sequencers = []
    tcp_cntrl_nodes = []

    # For an odd number of CPUs, still create the right number of controllers
    TCC_bits = int(math.log(options.num_tccs, 2))

    for i in range(options.num_compute_units):
        tcp_cntrl = TCPCntrl(
            TCC_select_num_bits=TCC_bits, issue_latency=1, number_of_TBEs=2560
        )
        # TBEs set to max outstanding requests
        tcp_cntrl.create(options, ruby_system, system)
        tcp_cntrl.WB = options.WB_L1
        tcp_cntrl.disableL1 = options.noL1
        tcp_cntrl.L1cache.tagAccessLatency = options.TCP_latency
        tcp_cntrl.L1cache.dataAccessLatency = options.TCP_latency

        exec("ruby_system.tcp_cntrl%d = tcp_cntrl" % i)
        #
        # Add controllers and sequencers to the appropriate lists
        #
        tcp_sequencers.append(tcp_cntrl.coalescer)
        tcp_cntrl_nodes.append(tcp_cntrl)

        # Connect the TCP controller to the ruby network
        tcp_cntrl.requestFromTCP = MessageBuffer(ordered=True)
        tcp_cntrl.requestFromTCP.out_port = network.in_port

        tcp_cntrl.responseFromTCP = MessageBuffer(ordered=True)
        tcp_cntrl.responseFromTCP.out_port = network.in_port

        tcp_cntrl.unblockFromCore = MessageBuffer()
        tcp_cntrl.unblockFromCore.out_port = network.in_port

        tcp_cntrl.probeToTCP = MessageBuffer(ordered=True)
        tcp_cntrl.probeToTCP.in_port = network.out_port

        tcp_cntrl.responseToTCP = MessageBuffer(ordered=True)
        tcp_cntrl.responseToTCP.in_port = network.out_port

        tcp_cntrl.mandatoryQueue = MessageBuffer()

    return (tcp_sequencers, tcp_cntrl_nodes)


def construct_sqcs(options, system, ruby_system, network):
    sqc_sequencers = []
    sqc_cntrl_nodes = []

    # For an odd number of CPUs, still create the right number of controllers
    TCC_bits = int(math.log(options.num_tccs, 2))

    for i in range(options.num_sqc):
        sqc_cntrl = SQCCntrl(TCC_select_num_bits=TCC_bits)
        sqc_cntrl.create(options, ruby_system, system)

        exec("ruby_system.sqc_cntrl%d = sqc_cntrl" % i)
        #
        # Add controllers and sequencers to the appropriate lists
        #
        sqc_sequencers.append(sqc_cntrl.sequencer)
        sqc_cntrl_nodes.append(sqc_cntrl)

        # Connect the SQC controller to the ruby network
        sqc_cntrl.requestFromSQC = MessageBuffer(ordered=True)
        sqc_cntrl.requestFromSQC.out_port = network.in_port

        sqc_cntrl.probeToSQC = MessageBuffer(ordered=True)
        sqc_cntrl.probeToSQC.in_port = network.out_port

        sqc_cntrl.responseToSQC = MessageBuffer(ordered=True)
        sqc_cntrl.responseToSQC.in_port = network.out_port

        sqc_cntrl.mandatoryQueue = MessageBuffer()

    return (sqc_sequencers, sqc_cntrl_nodes)


def construct_scalars(options, system, ruby_system, network):
    scalar_sequencers = []
    scalar_cntrl_nodes = []

    # For an odd number of CPUs, still create the right number of controllers
    TCC_bits = int(math.log(options.num_tccs, 2))

    for i in range(options.num_scalar_cache):
        scalar_cntrl = SQCCntrl(TCC_select_num_bits=TCC_bits)
        scalar_cntrl.create(options, ruby_system, system)

        exec("ruby_system.scalar_cntrl%d = scalar_cntrl" % i)

        scalar_sequencers.append(scalar_cntrl.sequencer)
        scalar_cntrl_nodes.append(scalar_cntrl)

        scalar_cntrl.requestFromSQC = MessageBuffer(ordered=True)
        scalar_cntrl.requestFromSQC.out_port = network.in_port

        scalar_cntrl.probeToSQC = MessageBuffer(ordered=True)
        scalar_cntrl.probeToSQC.in_port = network.out_port

        scalar_cntrl.responseToSQC = MessageBuffer(ordered=True)
        scalar_cntrl.responseToSQC.in_port = network.out_port

        scalar_cntrl.mandatoryQueue = MessageBuffer()

    return (scalar_sequencers, scalar_cntrl_nodes)


def construct_cmdprocs(options, system, ruby_system, network):
    cmdproc_sequencers = []
    cmdproc_cntrl_nodes = []

    # For an odd number of CPUs, still create the right number of controllers
    TCC_bits = int(math.log(options.num_tccs, 2))

    for i in range(options.num_cp):
        tcp_ID = options.num_compute_units + i
        sqc_ID = options.num_sqc + i

        tcp_cntrl = TCPCntrl(
            TCC_select_num_bits=TCC_bits, issue_latency=1, number_of_TBEs=2560
        )
        # TBEs set to max outstanding requests
        tcp_cntrl.createCP(options, ruby_system, system)
        tcp_cntrl.WB = options.WB_L1
        tcp_cntrl.disableL1 = options.noL1
        tcp_cntrl.L1cache.tagAccessLatency = options.TCP_latency
        tcp_cntrl.L1cache.dataAccessLatency = options.TCP_latency

        exec("ruby_system.tcp_cntrl%d = tcp_cntrl" % tcp_ID)
        #
        # Add controllers and sequencers to the appropriate lists
        #
        cmdproc_sequencers.append(tcp_cntrl.sequencer)
        cmdproc_cntrl_nodes.append(tcp_cntrl)

        # Connect the CP (TCP) controllers to the ruby network
        tcp_cntrl.requestFromTCP = MessageBuffer(ordered=True)
        tcp_cntrl.requestFromTCP.out_port = network.in_port

        tcp_cntrl.responseFromTCP = MessageBuffer(ordered=True)
        tcp_cntrl.responseFromTCP.out_port = network.in_port

        tcp_cntrl.unblockFromCore = MessageBuffer(ordered=True)
        tcp_cntrl.unblockFromCore.out_port = network.in_port

        tcp_cntrl.probeToTCP = MessageBuffer(ordered=True)
        tcp_cntrl.probeToTCP.in_port = network.out_port

        tcp_cntrl.responseToTCP = MessageBuffer(ordered=True)
        tcp_cntrl.responseToTCP.in_port = network.out_port

        tcp_cntrl.mandatoryQueue = MessageBuffer()

        sqc_cntrl = SQCCntrl(TCC_select_num_bits=TCC_bits)
        sqc_cntrl.create(options, ruby_system, system)

        exec("ruby_system.sqc_cntrl%d = sqc_cntrl" % sqc_ID)
        #
        # Add controllers and sequencers to the appropriate lists
        #
        cmdproc_sequencers.append(sqc_cntrl.sequencer)
        cmdproc_cntrl_nodes.append(sqc_cntrl)

    return (cmdproc_sequencers, cmdproc_cntrl_nodes)


def construct_tccs(options, system, ruby_system, network):
    tcc_cntrl_nodes = []

    for i in range(options.num_tccs):
        tcc_cntrl = TCCCntrl(l2_response_latency=options.TCC_latency)
        tcc_cntrl.create(options, ruby_system, system)

        tcc_cntrl.l2_response_latency = options.TCC_latency
        tcc_cntrl.glc_atomic_latency = options.glc_atomic_latency
        tcc_cntrl_nodes.append(tcc_cntrl)
        tcc_cntrl.number_of_TBEs = 2560 * options.num_compute_units
        # the number_of_TBEs is inclusive of TBEs below

        # Connect the TCC controllers to the ruby network
        tcc_cntrl.requestFromTCP = MessageBuffer(ordered=True)
        tcc_cntrl.requestFromTCP.in_port = network.out_port

        tcc_cntrl.responseToCore = MessageBuffer(ordered=True)
        tcc_cntrl.responseToCore.out_port = network.in_port

        tcc_cntrl.probeFromNB = MessageBuffer()
        tcc_cntrl.probeFromNB.in_port = network.out_port


        tcc_cntrl.triggerQueue = MessageBuffer(ordered=True)

        tcc_cntrl.connect_cxl(ruby_system)
        exec("ruby_system.tcc_cntrl%d = tcc_cntrl" % i)

    return tcc_cntrl_nodes


def create_system(
    options, full_system, system, dma_devices, bootmem, ruby_system, cpus
):
    if buildEnv["PROTOCOL"] != "GPU_VIPER_CXL_MESIF":
        panic("This script requires the GPU_VIPER_CXL_MESIF protocol to be built.")

    cpu_sequencers = []

    #
    # Must create the individual controllers before the network to ensure the
    # controller constructors are called before the network constructor
    #

    # This is the base crossbar that connects the L3s, Dirs, and cpu/gpu
    # Clusters
    crossbar_bw = None
    mainCluster = None
    cpuCluster = None
    gpuCluster = None

    if hasattr(options, "bw_scalor") and options.bw_scalor > 0:
        # Assuming a 2GHz clock
        crossbar_bw = 16 * options.num_compute_units * options.bw_scalor
        mainCluster = Cluster(intBW=crossbar_bw)
        cpuCluster = Cluster(extBW=crossbar_bw, intBW=crossbar_bw, extLatency=options.to_dir_latency)
        gpuCluster = Cluster(extBW=crossbar_bw, intBW=crossbar_bw, extLatency=options.to_dir_latency)
    else:
        mainCluster = Cluster(intBW=8)  # 16 GB/s
        cpuCluster = Cluster(extBW=8, intBW=8, extLatency=options.to_dir_latency)  # 16 GB/s
        gpuCluster = Cluster(extBW=8, intBW=8, extLatency=options.to_dir_latency)  # 16 GB/s

    # Create CPU directory controllers
    dir_cntrl_nodes = construct_dirs(
        options, system, ruby_system, ruby_system.network
    )
    for dir_cntrl in dir_cntrl_nodes:
        mainCluster.add(dir_cntrl)

    (cp_sequencers, cp_cntrl_nodes) = construct_l1s(
        options, system, ruby_system, ruby_system.network
    )
    l2_cntrl = construct_l2(system, ruby_system, 0, options)

    cpu_sequencers.extend(cp_sequencers)
    for cp_cntrl in cp_cntrl_nodes:
        cpuCluster.add(cp_cntrl)
    cpuCluster.add(l2_cntrl)
    # Register CPUs and caches for each CorePair and directory (SE mode only)
    if not full_system:
        for i in range(options.num_cpus):
            FileSystemConfig.register_cpu(
                physical_package_id=0,
                core_siblings=range(options.num_cpus),
                core_id=i * 2,
                thread_siblings=[],
            )

            FileSystemConfig.register_cache(
                level=0,
                idu_type="Data",
                size=options.l1d_size,
                line_size=options.cacheline_size,
                assoc=options.l1d_assoc,
                cpus=[i * 2],
            )

        for i in range(options.num_dirs):
            FileSystemConfig.register_cache(
                level=2,
                idu_type="Unified",
                size=options.l3_size,
                line_size=options.cacheline_size,
                assoc=options.l3_assoc,
                cpus=[n for n in range(options.num_cpus)],
            )

    # Create TCPs
    (tcp_sequencers, tcp_cntrl_nodes) = construct_tcps(
        options, system, ruby_system, ruby_system.network
    )
    cpu_sequencers.extend(tcp_sequencers)
    for tcp_cntrl in tcp_cntrl_nodes:
        gpuCluster.add(tcp_cntrl)

    # Create SQCs
    (sqc_sequencers, sqc_cntrl_nodes) = construct_sqcs(
        options, system, ruby_system, ruby_system.network
    )
    cpu_sequencers.extend(sqc_sequencers)
    for sqc_cntrl in sqc_cntrl_nodes:
        gpuCluster.add(sqc_cntrl)

    # Create Scalars
    (scalar_sequencers, scalar_cntrl_nodes) = construct_scalars(
        options, system, ruby_system, ruby_system.network
    )
    cpu_sequencers.extend(scalar_sequencers)
    for scalar_cntrl in scalar_cntrl_nodes:
        gpuCluster.add(scalar_cntrl)

    # Create command processors
    (cmdproc_sequencers, cmdproc_cntrl_nodes) = construct_cmdprocs(
        options, system, ruby_system, ruby_system.network
    )
    cpu_sequencers.extend(cmdproc_sequencers)
    for cmdproc_cntrl in cmdproc_cntrl_nodes:
        gpuCluster.add(cmdproc_cntrl)

    # Create TCCs
    tcc_cntrl_nodes = construct_tccs(
        options, system, ruby_system, ruby_system.network
    )
    for tcc_cntrl in tcc_cntrl_nodes:
        gpuCluster.add(tcc_cntrl)

    for i, dma_device in enumerate(dma_devices):

        dma_seq = DMASequencer(version=i, ruby_system=ruby_system)
        dma_cntrl = GPU_VIPER_CXL_MESIF_DMA_Controller(
            version=i, dma_sequencer=dma_seq, ruby_system=ruby_system
        )
        exec("system.dma_cntrl%d = dma_cntrl" % i)

        # IDE doesn't have a .type but seems like everything else does.
        if not hasattr(dma_device, "type"):
            exec("system.dma_cntrl%d.dma_sequencer.in_ports = dma_device" % i)
        elif dma_device.type == "MemTest":
            exec(
                "system.dma_cntrl%d.dma_sequencer.in_ports = dma_devices.test"
                % i
            )
        else:
            exec(
                "system.dma_cntrl%d.dma_sequencer.in_ports = dma_device.dma"
                % i
            )

        dma_cntrl.requestToDir = MessageBuffer(buffer_size=0)
        dma_cntrl.requestToDir.out_port = ruby_system.network.in_port
        dma_cntrl.responseFromDir = MessageBuffer(buffer_size=0)
        dma_cntrl.responseFromDir.in_port = ruby_system.network.out_port
        dma_cntrl.mandatoryQueue = MessageBuffer(buffer_size=0)
        gpuCluster.add(dma_cntrl)

    # Add cpu/gpu clusters to main cluster
    mainCluster.add(cpuCluster)
    mainCluster.add(gpuCluster)


    ruby_system.network.number_of_virtual_networks = 17

    return (cpu_sequencers, dir_cntrl_nodes, mainCluster)
