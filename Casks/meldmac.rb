cask "meldmac" do
  version "0.2.0"
  sha256 "b9d2794a82363593b972013346c0db06c67a714bf8d100daf7a075adbf30d4e5"

  url "https://github.com/melichron/meld-macos-silicon-native/releases/download/v#{version}/MeldMac-#{version}-arm64.dmg"
  name "MeldMac"
  desc "Compare and merge files and folders"
  homepage "https://github.com/melichron/meld-macos-silicon-native"

  depends_on arch: :arm64
  depends_on macos: ">= :sonoma"

  app "MeldMac.app"
end
