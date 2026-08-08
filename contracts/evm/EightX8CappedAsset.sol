// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Burnable} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Burnable.sol";
import {ERC20Capped} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Capped.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

/// @title EightX8CappedAsset
/// @notice Testnet-first implementation candidate for the 8x8 market-asset family.
/// @dev The immutable cap is 8,888,888 whole tokens. The constructor mints the
///      full cap to the owner treasury. Burning reduces totalSupply and reopens
///      mint headroom, but minting can never push totalSupply above the cap.
///      This contract does not set or control secondary-market price.
contract EightX8CappedAsset is ERC20, ERC20Burnable, ERC20Capped, AccessControl {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant POLICY_ADMIN_ROLE = keccak256("POLICY_ADMIN_ROLE");

    uint8 private immutable _assetDecimals;
    uint256 public immutable wholeTokenCap;

    event PolicyVersionRecorded(bytes32 indexed policyDigest, string policyVersion);

    error ZeroAddress();

    constructor(
        string memory name_,
        string memory symbol_,
        uint8 decimals_,
        address ownerTreasury_,
        address policyAdmin_
    )
        ERC20(name_, symbol_)
        ERC20Capped(8_888_888 * (10 ** decimals_))
    {
        if (ownerTreasury_ == address(0) || policyAdmin_ == address(0)) revert ZeroAddress();
        _assetDecimals = decimals_;
        wholeTokenCap = 8_888_888;

        _grantRole(DEFAULT_ADMIN_ROLE, policyAdmin_);
        _grantRole(POLICY_ADMIN_ROLE, policyAdmin_);
        _grantRole(MINTER_ROLE, policyAdmin_);

        _mint(ownerTreasury_, cap());
    }

    function decimals() public view override returns (uint8) {
        return _assetDecimals;
    }

    /// @notice Mint only within the immutable cap. If the full cap is initially
    ///         minted, new minting is possible only after supply has been burned.
    function mint(address to, uint256 amount) external onlyRole(MINTER_ROLE) {
        if (to == address(0)) revert ZeroAddress();
        _mint(to, amount);
    }

    /// @notice Records the hash/version of an approved off-chain tokenomics policy.
    /// @dev Policy data such as primary-sale configuration, allocations and fees is
    ///      governed separately. Recording a digest does not mutate market price.
    function recordPolicy(bytes32 policyDigest, string calldata policyVersion)
        external
        onlyRole(POLICY_ADMIN_ROLE)
    {
        emit PolicyVersionRecorded(policyDigest, policyVersion);
    }

    function _update(address from, address to, uint256 value)
        internal
        override(ERC20, ERC20Capped)
    {
        super._update(from, to, value);
    }
}
