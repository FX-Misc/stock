#!/bin/sh


codes="
^N225
^DJI
^GSPC
^IXIC
^FTSE
JPY=X
GBPUSD=X
EURUSD=X
^VIX
^TNX
GC=F
CL=F
"
for code in $codes;do
Rscript hist_dow.R $code  
done
