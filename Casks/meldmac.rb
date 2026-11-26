cask "meldmac" do
  version "0.2.1"
  sha256 "e40f7d862e9ab5ba6a1e6583525a3218b244b292cdb9e30ee1680c2adbcde7f3"

  url "https://github.com/melichron/meld-macos-silicon-native/releases/download/v#{version}/MeldMac-#{version}-arm64.dmg"
  name "MeldMac"
  desc "Compare and merge files and folders"
  homepage "https://github.com/melichron/meld-macos-silicon-native"

  depends_on arch: :arm64
  depends_on macos: :sonoma

  app "MeldMac.app"
end
