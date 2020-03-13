#!/bin/bash
echo 'starting'
outdir='out_dir'
mkdir -p $outdir
tmpdir=$(mktemp -d /tmp/abc-script.XXXXXX)
backpipe=$tmpdir/backpipe
mkfifo $backpipe

# basic two way nc with a backpipe.
# I've added some tee commands to dump stuff to disk.
#
# the tail -fn+3 is there to skip the first two lines, these are 
# meant for a human, not the real server.
# line buffering was an issue, so I used stdbuf to disable that.
#
# server_to_client.b
echo 'netcatting'
nc 3.93.128.89 12022  0< $backpipe \
    | tee $outdir/client_to_server_with_auth_code.bin \
    | stdbuf -i0 -o0 tail -fn+3 \
    | tee $outdir/client_to_server.bin \
    | nc  3.93.128.89 12021 \
    | tee $outdir/server_to_client.bin 1> $backpipe 
#stdbuf -i0 tail -fn0 out_dir/client_to_server.bin server_to_client.bin | xxd&
#stdbuf -i0 tail -fn0 out_dir/client_to_server_with_auth_code.bin  | stdbuf -i0 head -n1 &
