	  program NJ_DegreeDays
!**********************************************************************************
! Program developed by Logan Soldo 
! Latest version September 25th, 2019
! Program was developed for Snow Depth Thesis Project. 
! This is an unsophisticated, brute force program.  


!VARIABLES

	  implicit none 
 
 	  
	  integer i, j, k, l,m,p,n,miss_total
	  integer Datestring,year,month,MonthDay,day, julian

!	  integer station_num,station_10,station_25,station_50,station_100
	  real  TMax,TAvg,TMin,Base,yearReal,Tmiss,avg,GDD(366),W,AnnGDD(6),A,Day_avg(366)

	  ! real GDH(24), GDD(365,24),Daily_GDD(365),total_GDD(80),Base,total_100(80)
	  ! real total_GDH(80)

	 character(len=11) Station,Station_type
	 character(len=2) State
	 character(len=500) :: data_input,inputfile, outputfile, outputfile2,outputfile3,outputfile4,outputfile5,outputfile6
	  namelist /cdh_nml/ inputfile,outputfile, outputfile2,outputfile3,outputfile4,outputfile5,outputfile6,Base

open(33,file='cdh.nml',status='old')
read(33,nml=cdh_nml,end=55)
55 close(33)
write(*,nml=cdh_nml)
	  	 

	  
	  open(10, file=inputfile,status="old")
	  open(20, file=outputfile,status="replace")      ! Split Date
	  open(30, file=outputfile2,status="replace")	  ! Annual GDD
	  open(40, file=outputfile3,status="replace")	  ! Daily GDD
	  open(50, file=outputfile4,status="replace")	  ! Daily Avg
	  open(100,file=outputfile5,status="replace")	  ! Stats	  
	  Open(200,file=outputfile6, status = "replace")
		
 do k=1,6
	AnnGDD(k) = 0
 enddo

Tmiss = 999
! Extract the datestring to yyyy,mm,dd
! Adding Julian day counter.
		julian = 0
		Do m=1,100000
	!			print(200)
				read(10,*,end=15) Station,State,Datestring,Station_type,TMax,TMin,TAvg
				if (TAVG .ne. Tmiss) then
					TMax = (TMax-32)/1.8
					TMin = (TMin-32)/1.8
					TAvg = (TAvg-32)/1.8
				endif
			!	read(10,*,end=15) data_input
			!	write(20,*) Station,State,Datestring,Station_type,TMax,TMin,TAvg
	!			write(*,*) State
		!		read(10,*,end=15) Datestring,TMax,TMin,TAvg
				yearReal = Datestring/10000
				year= int(yearReal)
				
				MonthDay=mod(Datestring,10000)
				Month= MonthDay/100
							
				Day= mod(MonthDay,100)				
				
				julian = julian + 1
				

				! if ((month .EQ. 2) .and. (day .eq. 29))then
					! write(29,1000) Datestring,year,month,day,hour,temp,qtemp,dewpt,qdewpt,slp,qslp,rh
				! else			
				 write(20,1100) Station,State,Station_type,Datestring,year,month,day,julian,TMax,TMin,TAvg
				
				if ((year .ne. 2016) .and. (month .eq. 2) .and. (day .eq. 28)) then
					julian = 60
					write(20,1100) Station,State,Station_type,Datestring,year,2,29,julian,Tmiss,Tmiss,Tmiss
				endif
				if ((Month .eq. 12) .and. (day .eq. 31)) then
					julian = 0
				endif
				! endif
				
		enddo
		
15 		close(10)
	    rewind(20)				
		!!!!!!!!! Baskerville-Emin method		
		
	do k = 1,6	
		do i = 1,366
			read(20,1100,end=16) Station,State,Station_type,Datestring,year,month,day,julian,TMax,TMin,TAvg
			if (TAvg .ne. TMiss) then
				if (TAvg .ne. 999.00) then
					if (TMax .GT. Base) then
						avg = (TMax + TMin)/2
						if (TMin .ge. Base) then
							GDD(i) = avg - Base
						else
							W=(TMax-TMin)/2
							A=ASIN((Base-avg)/W)
							GDD(i)=(W*COS(A)-(Base-Avg)*(3.14/2-A))/3.14
						endif
					else
						GDD(i) = 0
					endif
				endif
			
				AnnGDD(k) = AnnGDD(k) + GDD(i)
			else
				miss_total = miss_total + 1
			endif

			
			write(40,*) Station, Station_type, Datestring,year,month,day,julian,AnnGDD(k)

		enddo
		write(30,*) year,k,AnnGDD(k)
	enddo
16 	close(20)

	write(100,*) "Missing Total", miss_total
	
	!!!!! TO DO: Get the daily average degree days. i.e. average GDD on July 2nd.!!!!!!!
	! do k = 1,6
		! do i = 1,366
	do i = 1,366
		Day_avg(i) = sum(GDD,i)/k
		write(50,*) Station, Station_type, julian, Day_avg(i)
	enddo			


1000 format(a11,a4,I8,a11,3(f10.2))
1100 format (a11,a4,a14,I10,4(I10),3(f10.2))



end
	   
