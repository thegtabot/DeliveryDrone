# Paths and Variables
$userProfile = [Environment]::GetFolderPath("UserProfile")
$githubConfigPath = Join-Path -Path $userProfile -ChildPath "OneDrive\Documents\GitHub\DeliveryDrone\drone_network_config\DRONE.conf"
$wireguardConfigDir = "C:\Program Files\WireGuard\Data\Configurations"  # Default WireGuard directory for configuration files
$newConfigFilePath = Join-Path -Path $wireguardConfigDir -ChildPath "NewClient.conf"
$assignedIpsPath = Join-Path -Path $userProfile -ChildPath "OneDrive\Documents\GitHub\DeliveryDrone\drone_network_config\assigned_ips.txt"

# Verify the GitHub configuration file exists
if (!(Test-Path -Path $githubConfigPath)) {
    Write-Output "Error: GitHub configuration file not found at $githubConfigPath."
    exit
}

# Load the existing assigned IPs from the file
$assignedIPs = @()
if (Test-Path -Path $assignedIpsPath) {
    $assignedIPs = Get-Content -Path $assignedIpsPath
}

# Function to find the next available IP address
$subnetBase = "10.0.0."
function Get-NextAvailableIP {
    for ($i = 1; $i -lt 255; $i++) {
        $newIP = "$subnetBase$i"
        # Ensure that the new IP is not already taken, not in the assigned list, and not one of the fixed IPs
        if ($newIP -notin $assignedIPs -and $newIP -ne "10.0.0.1" -and $newIP -ne "10.0.0.2" -and $newIP -ne "10.0.0.3") {
            # Save the new IP to the assigned list
            Add-Content -Path $assignedIpsPath -Value $newIP
            return $newIP
        }
    }
    throw "No available IP addresses in the subnet."
}

# Assign IP and generate keys
$newDeviceIp = Get-NextAvailableIP
try {
    $privateKey = & wg genkey
    $publicKey = echo $privateKey | & wg pubkey
}
catch {
    Write-Output "Error: Key generation failed. Ensure WireGuard CLI tools are installed."
    exit
}

# Generate the new [Interface] section with the assigned IP and keys
$newInterface = @"
[Interface]
Address = $newDeviceIp/24
PrivateKey = $privateKey
"@

# Define the static [Peer] section details
$peerDetails = @"
[Peer]
AllowedIPs = 10.0.0.0/24
Endpoint = 73.250.42.153:51820
PublicKey = XpLRFyvQGfAxqLpdmbY32bz53rmHjrxdCEJb1/76llk=
"@

# Combine [Interface] and [Peer] sections into the new configuration file
try {
    Set-Content -Path $newConfigFilePath -Value $newInterface
    Add-Content -Path $newConfigFilePath -Value $peerDetails
}
catch {
    Write-Output "Error: Unable to create or modify the configuration file. Run as administrator."
    exit
}

# Notify the user of the new config details
Write-Output "New Device Configuration created at $newConfigFilePath"
Write-Output "Assigned IP: $newDeviceIp"
Write-Output "Private Key: $privateKey"
Write-Output "Public Key: $publicKey"
