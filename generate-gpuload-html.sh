#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
template="${script_dir}/gpuload-embed.template.html"
output="${1:-${script_dir}/gpuload-embed.html}"

if [[ ! -f "${template}" ]]; then
  printf 'Template not found: %s\n' "${template}" >&2
  exit 1
fi
if ! command -v /share/apps/admin/tools/gpuload >/dev/null 2>&1; then
  printf 'gpuload is not available in PATH. Run this script on a login node.\n' >&2
  exit 1
fi

output_dir="$(dirname -- "${output}")"
mkdir -p -- "${output_dir}"
snapshot_file="$(mktemp)"
encoded_file="$(mktemp)"
output_tmp="$(mktemp "${output}.tmp.XXXXXX")"
trap 'rm -f -- "${snapshot_file}" "${encoded_file}" "${output_tmp}"' EXIT

/share/apps/admin/tools/gpuload > "${snapshot_file}"
base64 < "${snapshot_file}" | tr -d '\n' > "${encoded_file}"
snapshot_b64="$(<"${encoded_file}")"

if [[ "$(grep -o '__GPULOAD_SNAPSHOT_BASE64__' "${template}" | wc -l)" -ne 1 ]]; then
  printf 'Template must contain exactly one snapshot placeholder.\n' >&2
  exit 1
fi

sed "s|__GPULOAD_SNAPSHOT_BASE64__|${snapshot_b64}|" "${template}" > "${output_tmp}"
chmod 0644 "${output_tmp}"
mv -f -- "${output_tmp}" "${output}"
printf 'Generated %s\n' "${output}"
