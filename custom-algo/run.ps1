$scriptPath = Split-Path -parent $PSCommandPath;
$algoPath = "$scriptPath\custom_algo.py"

py -3 $algoPath
