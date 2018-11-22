## Von Neumann virtual machine
-----------

### Summary
Machine accepts as an input binary files prepared by asm interpreter. These files contain:
* own memory needed for execution (runtime memory cost is O(1))
* pseudo-machine code

Then the VM executes binaries according to the following principles:
1) Addressability principle
2) Consistency principle
3) Sequential execution principle
4) Hard architecture principle

These principles characterize classic Von Neumann architecture.

VM supports labels, procedures and recursion.

### Theoretical aspects

[Von Neumann architecture](https://en.wikipedia.org/wiki/Von_Neumann_architecture) is the one that is used in almost all modern CPUs due to it's more easy to develop and use then alternative model, [Harvard architecture](https://en.wikipedia.org/wiki/Harvard_architecture) .

It can be characterized by 4 main principles.

**Addressability** principle means that you can get a physical location of any data or code in machine.

**Consistency** principle is about homogeneous structure of memory in such machines. This is because commands and data are stored together.

**Sequential execution** principle represents the idea of that the ordinary program flow is consistence. Commands execute in the same order as they're stored (and written)

**Hard architecture** principle focuses on that the machine's memory can't be increased during runtime. It's fixed and in case of VM, it's also built in binary file.


### Implementation overview

Binary file is produced by Interpreter defined in **interpreter.py** 
It supports certain set of commands that emulate main real assembly commands.
Here is the full list of them:

* add
* sub
* mul
* inp
* out
* j0
* j1
* jump
* call
* push
* pop
* ret
* halt
* load
* store