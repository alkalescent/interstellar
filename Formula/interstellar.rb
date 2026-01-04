# typed: false
# frozen_string_literal: true

# Homebrew formula for interstellar
# This formula can be used in a homebrew-tap repository
#
# Installation:
#   brew tap alkalescent/tap
#   brew install interstellar
#
# Or directly:
#   brew install alkalescent/tap/interstellar

class Interstellar < Formula
  include Language::Python::Virtualenv

  desc "CLI tool for managing cryptocurrency mnemonics using BIP39 and SLIP39 standards"
  homepage "https://github.com/alkalescent/interstellar"
  # url will be set by the tap's update script from GitHub releases
  url "https://github.com/alkalescent/interstellar/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "PLACEHOLDER_SHA256"
  license "MIT"
  head "https://github.com/alkalescent/interstellar.git", branch: "master"

  depends_on "python@3.13"

  def install
    virtualenv_install_with_resources
  end

  test do
    # Test version command
    assert_match(/\d+\.\d+\.\d+/, shell_output("#{bin}/interstellar version"))
    
    # Test help command shows expected subcommands
    help_output = shell_output("#{bin}/interstellar --help")
    assert_match "deconstruct", help_output
    assert_match "reconstruct", help_output
  end
end
