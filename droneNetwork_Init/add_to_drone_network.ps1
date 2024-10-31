# Variables
$wgConfigPath = "C:\Program Files\WireGuard\wg0.conf"  # Default WireGuard config path

# Get the device name
$newDeviceName = $env:COMPUTERNAME  # Use the system's hostname as the device name

# Define the subnet for the VPN
$subnetBase = "10.0.0."  # Base of the subnet
$subnetMask = 24  # Subnet mask (CIDR notation)

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
$privateKey = wg genkey
$publicKey = echo $privateKey | wg pubkey

# Create new device entry
$newDeviceEntry = @"
[Peer]
PublicKey = $publicKey
AllowedIPs = $newDeviceIp/32
"@

# Add new device to WireGuard configuration
Add-Content -Path $wgConfigPath -Value $newDeviceEntry

# Restart WireGuard service to apply changes
Stop-Service -Name "WireGuard" -Force
Start-Service -Name "WireGuard"

# Output the new device configuration
"New Device Configuration:"
"Device Name: $newDeviceName"
"Private Key: $privateKey"
"Public Key: $publicKey"
"Assigned IP: $newDeviceIp"
