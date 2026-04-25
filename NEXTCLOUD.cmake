# SPDX-FileCopyrightText: 2017 Nextcloud GmbH and Nextcloud contributors
# SPDX-FileCopyrightText: 2012 ownCloud GmbH
# SPDX-License-Identifier: GPL-2.0-or-later
#
# keep the application name and short name the same or different for dev and prod build
# or some migration logic will behave differently for each build
set( APPLICATION_NAME       "The Cloud Market" )
set( APPLICATION_SHORTNAME  "TheCloudMarket" )
set( APPLICATION_EXECUTABLE "nextcloud" )
set( APPLICATION_ICON_NAME  "TheCloudMarket" )

set( APPLICATION_CONFIG_NAME "nextcloud" )
set( APPLICATION_DOMAIN     "thecloud.market" )
set( APPLICATION_VENDOR     "The Cloud Market" )
set( APPLICATION_UPDATE_URL "https://thecloud.market/updates/filesync/" CACHE STRING "URL for updater" )
set( APPLICATION_HELP_URL   "https://thecloud.market/support" CACHE STRING "URL for the help menu" )

if(APPLE AND EXISTS "${CMAKE_SOURCE_DIR}/theme/colored/TheCloudMarket-macOS-icon.svg")
    set( APPLICATION_ICON_NAME "TheCloudMarket-macOS" )
    message("Using macOS-specific application icon: ${APPLICATION_ICON_NAME}")
endif()

set( APPLICATION_ICON_SET   "SVG" )
set( APPLICATION_SERVER_URL "" CACHE STRING "URL for the server to use. If entered, the UI field will be pre-filled with it" )
set( APPLICATION_SERVER_URL_ENFORCE ON ) # If set and APPLICATION_SERVER_URL is defined, the server can only connect to the pre-defined URL
set( APPLICATION_REV_DOMAIN "market.thecloud.filesync" )
set( DEVELOPMENT_TEAM "NKUJUXUJ3B" CACHE STRING "Apple Development Team ID" )
set( APPLICATION_VIRTUALFILE_SUFFIX "thecloudmarket" CACHE STRING "Virtual file suffix (not including the .)")
set( APPLICATION_OCSP_STAPLING_ENABLED OFF )
set( APPLICATION_FORBID_BAD_SSL OFF )

set( LINUX_PACKAGE_SHORTNAME "thecloudmarket" )
set( LINUX_APPLICATION_ID "${APPLICATION_REV_DOMAIN}.${LINUX_PACKAGE_SHORTNAME}")

set( THEME_CLASS            "NextcloudTheme" )
set( WIN_SETUP_BITMAP_PATH  "${CMAKE_SOURCE_DIR}/admin/win/nsi" )

set( MAC_INSTALLER_BACKGROUND_FILE "${CMAKE_SOURCE_DIR}/admin/osx/installer-background.png" CACHE STRING "The MacOSX installer background image")

# set( THEME_INCLUDE          "${OEM_THEME_DIR}/mytheme.h" )
# set( APPLICATION_LICENSE    "${OEM_THEME_DIR}/license.txt )

## Updater options
option( BUILD_UPDATER "Build updater" ON )

option( WITH_PROVIDERS "Build with providers list" ON )

option( ENFORCE_VIRTUAL_FILES_SYNC_FOLDER "Enforce use of virtual files sync folder when available" OFF )
option( DISABLE_VIRTUAL_FILES_SYNC_FOLDER "Disable use of virtual files sync folder even when available" OFF )

option(ENFORCE_SINGLE_ACCOUNT "Enforce use of a single account in desktop client" OFF)

option( DO_NOT_USE_PROXY "Do not use system wide proxy, instead always do a direct connection to server" OFF )

option( WIN_DISABLE_USERNAME_PREFILL "Do not prefill the Windows user name when creating a new account" OFF )

## Theming options
set(NEXTCLOUD_BACKGROUND_COLOR "#0f1629" CACHE STRING "Default background color")
set( APPLICATION_WIZARD_HEADER_BACKGROUND_COLOR "#0f1629" CACHE STRING "Hex color of the wizard header background")
set( APPLICATION_WIZARD_HEADER_TITLE_COLOR "#ffffff" CACHE STRING "Hex color of the text in the wizard header")
option( APPLICATION_WIZARD_USE_CUSTOM_LOGO "Use the logo from ':/client/theme/colored/wizard_logo.(png|svg)' else the default application icon is used" ON )

#
## Windows Shell Extensions & MSI - IMPORTANT: Generate new GUIDs for custom builds with "guidgen" or "uuidgen"
#
if(WIN32)
    # Context Menu — TCM-specific GUIDs (must differ from stock Nextcloud)
    set( WIN_SHELLEXT_CONTEXT_MENU_GUID      "{1A6F78B4-9AB5-466C-9836-E4622E02A6CA}" )

    # Overlays
    set( WIN_SHELLEXT_OVERLAY_GUID_ERROR     "{41CB87E8-41C8-46E0-B252-A4F0D69ED5EC}" )
    set( WIN_SHELLEXT_OVERLAY_GUID_OK        "{08D18E3D-EF75-4A1C-A554-8F625372C04A}" )
    set( WIN_SHELLEXT_OVERLAY_GUID_OK_SHARED "{F54A5704-B023-4C4B-89A0-1EDAF1B96863}" )
    set( WIN_SHELLEXT_OVERLAY_GUID_SYNC      "{49799314-D4BE-401E-AE60-EF239B91F814}" )
    set( WIN_SHELLEXT_OVERLAY_GUID_WARNING   "{31F2F7B9-16C4-4564-8BB2-FCEAE3CA8D1A}" )

    # MSI Upgrade Code (without brackets)
    set( WIN_MSI_UPGRADE_CODE                "75C06785-1385-448D-8EA9-B81794205122" )

    # Windows build options
    option( BUILD_WIN_MSI "Build MSI scripts and helper DLL" OFF )
    option( BUILD_WIN_TOOLS "Build Win32 migration tools" OFF )
endif()

if (APPLE AND CMAKE_OSX_DEPLOYMENT_TARGET VERSION_GREATER_EQUAL 11.0)
    option( BUILD_FILE_PROVIDER_MODULE "Build the macOS virtual files File Provider module" OFF )
endif()
