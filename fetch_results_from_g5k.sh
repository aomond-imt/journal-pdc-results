archive_name='topologies_results.tar.xz'
ssh nancy.grid5000.fr "tar --lzma -cf $archive_name -C results-reconfiguration-esds topologies/paper"
scp "nancy.grid5000.fr:/home/anomond/$archive_name" "$archive_name"
ssh nancy.grid5000.fr "rm $archive_name"

tar --lzma -xvf "./$archive_name"
rm "$archive_name"
