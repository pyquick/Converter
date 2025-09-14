# -*- coding: utf-8 -*-
import requests
import re
import locale
class UpdateManager:
    def __init__(self, current_version: str):
        self.current_version = self._parse_version(current_version)

    def _parse_version(self, version_str):
        # Handles versions like 2.0.0 and pre-release like 2.0.0B3
        parts = version_str.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid version string: {version_str}")

        major = int(parts[0])
        minor = int(parts[1])
        
        patch_part = parts[2]
        match = re.match(r'^(\d+)([a-zA-Z]*)(\d*)$', patch_part)
        
        if not match:
            raise ValueError(f"Invalid patch format in version string: {patch_part}")

        num_str, tag, pre_num_str = match.groups()
        patch = int(num_str)
        
        if tag:
            pre_release_tag = tag.lower()
            pre_release_num = int(pre_num_str) if pre_num_str else 0
            return (major, minor, patch, pre_release_tag, pre_release_num)
        else:
            # For stable releases, use empty string instead of 'z' to avoid type comparison issues
            return (major, minor, patch, '', 0)

    def check_for_updates(self, include_prerelease: bool) -> dict:
        try:
            from con import CON
            repo_owner = "pyquick"
            repo_name = "converter"
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"
            response = requests.get(url, timeout=10,headers=CON.headers)
           
            response.encoding = 'utf-8'
            response.raise_for_status()
            all_releases = response.json()

            latest_suitable_release = None
            latest_suitable_version = (0, 0, 0, '', 0)

            for release in all_releases:
                is_prerelease = release.get("prerelease", False)
                tag_name = release.get("tag_name", "0.0.0").lstrip('vV')

                if not tag_name:
                    continue
                
                if is_prerelease and not include_prerelease:
                    continue
                
                try:
                    release_version = self._parse_version(tag_name)
                except ValueError:
                    continue

                # Compare versions using a custom comparison function
                if self._compare_versions(release_version, latest_suitable_version) > 0:
                    latest_suitable_version = release_version
                    latest_suitable_release = release
            
            if latest_suitable_release and self._compare_versions(latest_suitable_version, self.current_version) > 0:
                latest_version_str = latest_suitable_release.get("tag_name", "0.0.0").lstrip('vV')
                return {
                    "status": "update_available",
                    "message": f"New version available: {latest_version_str}!",
                    "download_url": latest_suitable_release.get('html_url', ''),
                    "latest_version": latest_version_str,
                    "release_body": latest_suitable_release.get('body', '')
                }
            elif latest_suitable_release and self._compare_versions(latest_suitable_version, self.current_version) <= 0:
                return {
                    "status": "latest",
                    "message": f"You are running the latest version ({self._parse_version_to_str(self.current_version)}).",
                    "latest_version": self._parse_version_to_str(self.current_version)
                }
            else:
                return {
                    "status": "no_updates",
                    "message": "No suitable updates found.",
                    "latest_version": "N/A"
                }

        except requests.exceptions.RequestException as e:
            return {"status": "error", "message": f"Update check failed: {e}"}
        except ValueError as e:
            return {"status": "error", "message": f"Version parsing failed: {e}"}
        except Exception as e:
            return {"status": "error", "message": f"An unexpected error occurred: {e}"}
    
    def _compare_versions(self, version1, version2):
        """Custom version comparison function to handle tuple comparison issues"""
        major1, minor1, patch1, tag1, pre_num1 = version1
        major2, minor2, patch2, tag2, pre_num2 = version2
        
        # Compare major version
        if major1 != major2:
            return 1 if major1 > major2 else -1
        
        # Compare minor version
        if minor1 != minor2:
            return 1 if minor1 > minor2 else -1
        
        # Compare patch version
        if patch1 != patch2:
            return 1 if patch1 > patch2 else -1
        
        # Compare tags - stable releases (empty tag) are greater than pre-releases
        if tag1 == '' and tag2 != '':
            return 1
        elif tag1 != '' and tag2 == '':
            return -1
        elif tag1 != tag2:
            # Compare pre-release tags alphabetically
            return 1 if tag1 > tag2 else -1
        
        # Compare pre-release numbers
        if pre_num1 != pre_num2:
            return 1 if pre_num1 > pre_num2 else -1
        
        return 0

    def _parse_version_to_str(self, version_tuple: tuple) -> str:
        major, minor, patch, tag, pre_num = version_tuple
        if tag == '':
            return f"{major}.{minor}.{patch}"
        else:
            # If pre_num is 0, it might have been something like 'beta' without a number
            if pre_num == 0:
                return f"{major}.{minor}.{patch}{tag.upper()}"
            return f"{major}.{minor}.{patch}{tag.upper()}{pre_num}"
