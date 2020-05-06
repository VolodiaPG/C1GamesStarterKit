$scriptPath = Split-Path -parent $PSCommandPath;
$algoPath = "$scriptPath\strategy.py"

py -3 $algoPath
