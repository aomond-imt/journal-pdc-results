archive_name='topologies_results.tar'
ssh nancy.grid5000.fr "tar -cf $archive_name --exclude=debug.txt -C results-reconfiguration-esds topologies"
scp "nancy.grid5000.fr:/home/anomond/$archive_name" "$archive_name"
ssh nancy.grid5000.fr "rm $archive_name"

tar -xvf "./$archive_name"
rm "$archive_name"
