# Cache Design and Memory Hierarchy Simulator
## Project Overview
This project involves implementing a flexible cache and memory hierarchy simulator to compare the performance, area, and energy of different memory hierarchy configurations using a subset of the SPEC-2000 benchmark suite.

## Project Description
You will design a generic cache module that can be used at any level in a memory hierarchy (e.g., L1, L2, L3). The cache should support various configurations and parameters, including:
1 Size: Total bytes of data storage.
2 Associativity: The associativity of the cache (1 for direct-mapped).
3 Block Size: Number of bytes in a block.

### Replacement Policies
The simulator must implement two replacement policies:
1 LRU (Least-Recently-Used)
2 FIFO (First-In-First-Out)

### Write Policy
The cache uses a Write-Back + Write-Allocate (WBWA) policy:
1 Write-Allocate: Allocates a block on a write miss.
2 Write-Back: Updates the block in the cache and marks it dirty.

## Memory Hierarchy
The simulator should support multiple instances of the cache forming an overall memory hierarchy, handling requests from the CPU or other caches. When a cache miss occurs, the cache should allocate the required block following a two-step process:
1 Make Space: Evict a block if necessary.
2 Bring in Block: Fetch the block from the next level in the memory hierarchy.

## Outputs
The simulator should output:
1 Memory hierarchy configuration and trace filename.
2 Final contents of all caches.
3 Measurements including L1/L2 reads, misses, miss rates, writebacks, and total memory traffic.

## Running the Simulator
1 The project requires a Makefile for compilation.
2 The simulator should be compiled into an executable named sim_cache.
3 The simulator accepts 8 command-line arguments:

Detailed Information can be obtained from /MP1_Instructions.pdf
