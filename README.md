# ggdb_x86

GRB based graphical debugger, for debugging x86 asm code.

This tool starts gdb process in background and obtains references  
To read and write file descriptors of the GDB process.  
A write worker thread is created to write command to gdb process.  
And a read worker thread is created to read the command output.

User actions are converted into gdb commands and enqueued in write queue,  
Which is being processed by write worker thread. The write worker thread ultimately  
Writes the command to GDB process using write file descriptor reference.  

After sending the command the write thread enqueues a read request in read queue.  
The output is then processed by read thread and result is fetched and enqueued in result queue.  
The result queue is processed by UI thread, and displays the output
