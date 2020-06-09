#!/bin/bash

pgm=DegreeDays.exe

#set -x


datadir=/mnt/e/School/RutgersWork/DegreeDayAnalysis
outputdir=/mnt/e/School/RutgersWork/DegreeDayAnalysis




for run in CreamRidge Howell SeaGirt Wall


do

	for base in 2.0 4.0 5.0 7.0 10.0
	
	do

 mkdir -p /mnt/e/School/RutgersWork/DegreeDayAnalysis
   mkdir -p /mnt/e/School/RutgersWork/DegreeDayAnalysis/$run/Outputs
	   mkdir -p /mnt/e/School/RutgersWork/DegreeDayAnalysis/$run/Outputs/Annual
		mkdir -p /mnt/e/School/RutgersWork/DegreeDayAnalysis/$run/Outputs/Daily

	 mkdir -p /mnt/e/School/RutgersWork/DegreeDayAnalysis/$run/Junk


    
 for filein in `ls -d $datadir/$run/${run}.csv`
   

   do
      filename=`basename $filein|sed 's/\.csv//'`
	fileout=$outputdir/$run/Outputs/
	fileout2=$outputdir/$run/Outputs/Annual/
	fileout3=$outputdir/$run/Outputs/Daily/	
	fileout4=$outputdir/$run/Junk/

    echo $filename
	echo $fileout
	
	#      create the namelist file
      cat <<EOF > cdh.nml
&cdh_nml
inputfile="${filein}",
outputfile="${fileout}${run}_SplitCSV.txt",
outputfile2="${fileout2}${run}_AnnGDD_B${base}.txt",
outputfile3="${fileout3}${run}_DailyGDD_B${base}.txt",
outputfile4="${fileout}${run}_Stats.txt",
outputfile5="${fileout4}${run}_Junk.txt",
Base=$base
/
EOF

      #run the excutable
     ./$pgm
      
      if [ $? -ne 0 ]; then
        echo "$run finished with error"
         exit
      fi
   
	  
           
			done
		 done
      done


#rm -f data1.bin

echo "END OF SCRIPT at $(date)"
