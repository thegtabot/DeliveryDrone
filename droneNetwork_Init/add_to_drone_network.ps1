# Variables
$wgConfigPath = "C:\Program Files\WireGuard\Data\Configurations"  # Default WireGuard config path

# Get the device name
$newDeviceName = $env:COMPUTERNAME  # Use the system's hostname as the device name

# Define the subnet for the VPN
$subnetBase = "10.0.0."  # Base of the subnet
$subnetMask = 24  # Subnet mask (CIDR notation)

# Check if WireGuard config exists
if (!(Test-Path -Path $wgConfigPath)) {
    Write-Output "Error: WireGuard configuration file not found at $wgConfigPath."
    exit
}

# Function to find the next available IP address in the subnet
function Get-NextAvailableIP {
    $usedIPs = Get-Content -Path $wgConfigPath | Select-String -Pattern "AllowedIPs" | ForEach-Object {
        $_.ToString().Split("=", 2)[1].Trim() -replace "/.*", ""
    }

    for ($i = 1; $i -lt 255; $i++) {
        $newIP = $subnetBase + $i
        if ($newIP -notin $usedIPs) {
            return $newIP
        }
    }

    throw "No available IP addresses in the subnet."
}

# Get the next available IP address
$newDeviceIp = Get-NextAvailableIP

# Generate key pair for the new device
try {
    # Generate keys (requires WireGuard's command-line tools installed)
    $privateKey = & wg genkey
    $publicKey = echo $privateKey | & wg pubkey
}
catch {
    Write-Output "Error: Key generation failed. Ensure WireGuard CLI tools are installed."
    exit
}

# Create new device entry
$newDeviceEntry = @"
[Peer]
PublicKey = $publicKey
AllowedIPs = $newDeviceIp/32
"@

# Add new device to WireGuard configuration
try {
    Add-Content -Path $wgConfigPath -Value $newDeviceEntry
}
catch {
    Write-Output "Error: Unable to write to $wgConfigPath. Please run this script as administrator."
    exit
}

# Restart WireGuard service to apply changes
try {
    Stop-Service -Name "WireGuard" -Force
    Start-Service -Name "WireGuard"
}
catch {
    Write-Output "Error: Could not restart the WireGuard service. Ensure you have administrator privileges."
    exit
}

# Output the new device configuration
Write-Output "New Device Configuration:"
Write-Output "Device Name: $newDeviceName"
Write-Output "Private Key: $privateKey"
Write-Output "Public Key: $publicKey"
Write-Output "Assigned IP: $newDeviceIp"
