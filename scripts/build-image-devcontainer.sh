#!/usr/bin/env bash
set -euo pipefail

# build-image-devcontainer.sh — builda a imagem de referência do devcontainer
# (.devcontainer/Dockerfile-devcontainer), fora do docker-compose.
#
# Padrão (remoto): baixa .devcontainer/.env.example e
# .devcontainer/Dockerfile-devcontainer direto do repositório GitHub do
# devcontainer-ai-cli (branch configurável) e builda a partir deles — não
# depende de estar dentro de um clone do projeto, então funciona como
# downloader avulso (curl | bash), igual ao scripts/install.sh.
#
# --local: usa .devcontainer/.env e .devcontainer/Dockerfile-devcontainer já
# existentes no projeto local (mesmo diretório deste script), sem tocar no
# GitHub — para testar mudanças no Dockerfile antes de publicá-las.
#
# Qualquer opção não reconhecida abaixo é repassada ao "docker build" (ex.:
# --no-cache).

REPO_URL="https://github.com/scarlosfreitas/devcontainer-ai-cli.git"
BRANCH="main"
LOCAL_MODE=false
EXTRA_ARGS=()

usage() {
  cat <<'EOF'
Uso: build-image-devcontainer.sh [opções] [-- argumentos extras do docker build]

Opções:
  --local            Usa .devcontainer/.env e .devcontainer/Dockerfile-devcontainer
                      já existentes no projeto local, em vez de baixar do GitHub.
  --repo-url <url>   URL do repositório a baixar no modo padrão (default: oficial)
  --branch <nome>    Branch a baixar no modo padrão (default: main)
  -h, --help         Mostra esta ajuda

Por padrão (sem --local), baixa .devcontainer/.env.example e
.devcontainer/Dockerfile-devcontainer do repositório devcontainer-ai-cli no
GitHub e builda a imagem a partir deles, sem exigir um clone local do
projeto. Qualquer opção não reconhecida acima é repassada ao "docker build"
(ex.: --no-cache).
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --local) LOCAL_MODE=true; shift ;;
    --repo-url) REPO_URL="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) EXTRA_ARGS+=("$1"); shift ;;
  esac
done

log()  { printf '==> %s\n' "$*"; }
die()  { printf 'Erro: %s\n' "$*" >&2; exit 1; }

command -v docker >/dev/null 2>&1 || die "docker é obrigatório e não foi encontrado no PATH."

# Lê DOCKER_IMAGE_NAME/DOCKER_IMAGE_TAG de $3 (env file) e builda $2
# (Dockerfile) com contexto $1, marcando a imagem como nome:tag.
build_from() {
  local build_context="$1" dockerfile="$2" env_file="$3"

  [[ -f "$dockerfile" ]] || die "$dockerfile não encontrado."
  [[ -f "$env_file" ]] || die "$env_file não encontrado."

  local image_name image_tag
  image_name="$(grep -E '^DOCKER_IMAGE_NAME=' "$env_file" | tail -1 | cut -d= -f2- || true)"
  image_tag="$(grep -E '^DOCKER_IMAGE_TAG=' "$env_file" | tail -1 | cut -d= -f2- || true)"

  [[ -n "$image_name" && -n "$image_tag" ]] \
    || die "DOCKER_IMAGE_NAME e DOCKER_IMAGE_TAG precisam estar definidos em $env_file."

  local image_ref="${image_name}:${image_tag}"

  log "construindo $image_ref a partir de $dockerfile..."
  docker build \
    -f "$dockerfile" \
    -t "$image_ref" \
    "${EXTRA_ARGS[@]}" \
    "$build_context"

  log "imagem construída: $image_ref"
}

if [[ "$LOCAL_MODE" == true ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

  log "modo local: usando .devcontainer/.env e .devcontainer/Dockerfile-devcontainer de $PROJECT_DIR"
  build_from \
    "$PROJECT_DIR" \
    "$PROJECT_DIR/.devcontainer/Dockerfile-devcontainer" \
    "$PROJECT_DIR/.devcontainer/.env"
else
  command -v git >/dev/null 2>&1 || die "git é obrigatório e não foi encontrado no PATH."

  TMP_DIR="$(mktemp -d)"
  cleanup() { rm -rf "$TMP_DIR"; }
  trap cleanup EXIT

  log "baixando .devcontainer/ ($REPO_URL, branch $BRANCH)..."
  git clone --quiet --depth 1 --branch "$BRANCH" "$REPO_URL" "$TMP_DIR"

  build_from \
    "$TMP_DIR" \
    "$TMP_DIR/.devcontainer/Dockerfile-devcontainer" \
    "$TMP_DIR/.devcontainer/.env.example"
fi
