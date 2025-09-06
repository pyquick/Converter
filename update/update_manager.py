import requests
import re

class UpdateManager:
    def __init__(self, current_version: str):
        self.current_version = self._parse_version(current_version)

    def _parse_version(self, version_str):
        # Handles versions like 2.0.0 and pre-release like 2.0.0B1
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
            # 'z' ensures stable releases are considered "greater" than pre-releases
            return (major, minor, patch, 'z', 0)

    def check_for_updates(self, include_prerelease: bool) -> dict:
        try:
            repo_owner = "pyquick"
            repo_name = "converter"
            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases"
            response = requests.get(url, timeout=10)
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

                if release_version > latest_suitable_version:
                    latest_suitable_version = release_version
                    latest_suitable_release = release
            
            if latest_suitable_release and (latest_suitable_version > self.current_version):
                latest_version_str = latest_suitable_release.get("tag_name", "0.0.0").lstrip('vV')
                return {
                    "status": "update_available",
                    "message": f"New version available: {latest_version_str}!",
                    "download_url": latest_suitable_release.get('html_url', ''),
                    "latest_version": latest_version_str
                }
            elif latest_suitable_release and (latest_suitable_version <= self.current_version):
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
    
    def _parse_version_to_str(self, version_tuple: tuple) -> str:
        major, minor, patch, tag, pre_num = version_tuple
        if tag == 'z':
            return f"{major}.{minor}.{patch}"
        else:
            # If pre_num is 0, it might have been something like 'beta' without a number
            if pre_num == 0:
                return f"{major}.{minor}.{patch}{tag.upper()}"
            return f"{major}.{minor}.{patch}{tag.upper()}{pre_num}"
