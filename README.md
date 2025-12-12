# MTG Deck Storage API

API REST para gerenciar banco de cartas e decks de Magic: The Gathering. O sistema permite importar cartas da API Scryfall, criar e gerenciar decks, e realizar buscas avançadas.

## Tecnologias

- **FastAPI** - Framework web moderno e rápido para Python
- **MongoDB** - Banco de dados NoSQL para armazenamento flexível
- **Docker** - Containerização para ambiente isolado
- **Scryfall API** - Integração para buscar dados de cartas MTG
- **Motor** - Driver assíncrono para MongoDB
- **Pydantic** - Validação de dados e schemas

## Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.9+ (para desenvolvimento local)

## Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd MTG-deck-storage
```

2. Crie o arquivo `.env` na pasta `backend/`:
```env
MONGO_USER=seu_usuario
MONGO_PASS=sua_senha
MONGO_DB=mtg_database
MONGO_HOST=mongo
MONGO_PORT=27017
API_PORT=8000
```

3. Inicie os containers:
```bash
cd backend
docker-compose up -d
```

A API estará disponível em `http://localhost:8000`

## Documentação Interativa

Após iniciar a API, acesse:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Endpoints

### Status da API

#### `GET /`
Retorna o status da API e contadores.

**Resposta:**
```json
{
  "msg": "API funcionando!",
  "total_cards": 150,
  "total_decks": 10
}
```

---

## Endpoints de Cartas

### `GET /cards/test`
Testa a conexão com MongoDB.

**Resposta:**
```json
{
  "mongo_status": "ok",
  "total_cards": 150
}
```

### `POST /cards/import`
Importa uma carta da Scryfall pelo nome.

**Body:**
```json
{
  "name": "Lightning Bolt"
}
```

**Resposta (201):**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "Lightning Bolt",
  "scryfall_id": "abc123...",
  "mana_cost": "{R}",
  "type_line": "Instant",
  "oracle_text": "Lightning Bolt deals 3 damage...",
  "colors": ["R"],
  "rarity": "common",
  "image_uris": {
    "small": "https://cards.scryfall.io/small/...",
    "normal": "https://cards.scryfall.io/normal/...",
    "large": "https://cards.scryfall.io/large/..."
  },
  "prices": {
    "usd": "0.50",
    "usd_foil": "5.00"
  }
}
```

### `POST /cards/import-bulk`
Importa múltiplas cartas de uma vez (máximo 100).

**Body:**
```json
{
  "names": [
    "Lightning Bolt",
    "Counterspell",
    "Dark Ritual"
  ]
}
```

**Resposta (200):**
```json
{
  "total": 3,
  "success": 2,
  "failed": 1,
  "successful_cards": [...],
  "failed_cards": [
    {
      "name": "Invalid Card",
      "error": "Carta 'Invalid Card' não encontrada na Scryfall"
    }
  ]
}
```

### `GET /cards/{scryfall_id}`
Busca uma carta pelo scryfall_id.

**Resposta:**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "Lightning Bolt",
  "scryfall_id": "abc123...",
  ...
}
```

### `GET /cards/`
Busca cartas com filtros opcionais.

**Query Parameters:**
- `name` (opcional): Busca parcial por nome
- `colors` (opcional): Filtro por cores (ex: `R,U` ou `R,U,W`)
- `type_line` (opcional): Filtro por tipo (ex: `Creature`)
- `rarity` (opcional): Filtro por raridade
- `limit` (padrão: 50, máximo: 100): Número de resultados
- `skip` (padrão: 0): Paginação

**Exemplo:**
```
GET /cards/?name=bolt&colors=R&limit=10
```

**Resposta:**
```json
{
  "total": 5,
  "limit": 10,
  "skip": 0,
  "cards": [...]
}
```

### `GET /cards/all`
Retorna todas as cartas salvas com paginação.

**Query Parameters:**
- `limit` (padrão: 100, máximo: 100): Número de resultados
- `skip` (padrão: 0): Paginação

**Exemplo:**
```
GET /cards/all?limit=50&skip=0
```

### `GET /cards/count/total`
Retorna o total de cartas no banco.

**Resposta:**
```json
{
  "total_cards": 150
}
```

---

## Endpoints de Decks

### `POST /decks/`
Cria um novo deck.

**Body:**
```json
{
  "name": "Red Deck Wins",
  "format": "commander",
  "cards": [
    {
      "scryfall_id": "abc123...",
      "quantity": 4
    },
    {
      "scryfall_id": "def456...",
      "quantity": 2
    }
  ]
}
```

**Resposta (201):**
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "Red Deck Wins",
  "format": "commander",
  "cards": [...],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

**Formatos aceitos:** `commander`, `standard`, `modern`, `legacy`, `vintage`, `pauper`, `bulk`

### `POST /decks/import-bulk`
Importa múltiplos decks de uma vez (máximo 100).

**Body:**
```json
{
  "decks": [
    {
      "name": "Deck 1",
      "format": "commander",
      "cards": [...]
    },
    {
      "name": "Deck 2",
      "format": "modern",
      "cards": [...]
    }
  ]
}
```

**Resposta (200):**
```json
{
  "total": 2,
  "success": 1,
  "failed": 1,
  "successful_decks": [...],
  "failed_decks": [
    {
      "name": "Deck Duplicado",
      "error": "Já existe um deck com o nome 'Deck Duplicado'"
    }
  ]
}
```

### `GET /decks/`
Lista todos os decks com filtros opcionais.

**Query Parameters:**
- `format` (opcional): Filtrar por formato
- `limit` (padrão: 50, máximo: 100): Número de resultados
- `skip` (padrão: 0): Paginação

**Exemplo:**
```
GET /decks/?format=commander&limit=20
```

**Resposta:**
```json
{
  "total": 10,
  "limit": 20,
  "skip": 0,
  "decks": [...]
}
```

### `GET /decks/{deck_id}`
Busca um deck pelo ID com todas as cartas expandidas.

**Resposta:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "deck_id": "507f1f77bcf86cd799439011",
  "name": "Red Deck Wins",
  "format": "commander",
  "cards": [
    {
      "_id": "...",
      "name": "Lightning Bolt",
      "scryfall_id": "abc123...",
      "mana_cost": "{R}",
      "image_uris": {...},
      "quantity": 4
    }
  ],
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

### `GET /decks/by-name/{deck_name}`
Busca um deck pelo nome com todas as cartas expandidas.

**Exemplo:**
```
GET /decks/by-name/Red%20Deck%20Wins
```

### `PUT /decks/{deck_id}`
Atualiza um deck.

**Body:**
```json
{
  "name": "Novo Nome",
  "format": "modern",
  "cards": [...]
}
```

**Nota:** Todos os campos são opcionais. Apenas os campos enviados serão atualizados.

### `PUT /decks/by-name/{deck_name}`
Atualiza um deck pelo nome.

### `DELETE /decks/{deck_id}`
Deleta um deck.

**Resposta:** 204 No Content

### `DELETE /decks/by-name/{deck_name}`
Deleta um deck pelo nome.

---

## Gerenciamento de Cartas em Decks

### `POST /decks/{deck_id}/cards`
Adiciona ou atualiza uma carta no deck.

**Body:**
```json
{
  "scryfall_id": "abc123...",
  "quantity": 2
}
```

**Nota:** Se a carta já existir no deck, a quantidade será somada.

### `PUT /decks/{deck_id}/cards/{scryfall_id}`
Atualiza a quantidade de uma carta no deck.

**Body:**
```json
{
  "quantity": 4
}
```

### `DELETE /decks/{deck_id}/cards/{scryfall_id}`
Remove uma carta do deck.

---

## Exportação de Decks

### `GET /decks/{deck_id}/export`
Exporta um deck em formato de texto (`[quantidade] [nome]`).

**Resposta (text/plain):**
```
4 Lightning Bolt
2 Counterspell
1 Dark Ritual
```

### `GET /decks/export-by-name/{deck_name}`
Exporta um deck pelo nome em formato de texto.

### `GET /decks/{deck_id}/export-json`
Exporta um deck em formato JSON (compatível com `DeckCreate`).

**Resposta:**
```json
{
  "name": "Red Deck Wins",
  "format": "commander",
  "cards": [
    {
      "scryfall_id": "abc123...",
      "quantity": 4
    }
  ]
}
```

### `GET /decks/export-by-name/{deck_name}/json`
Exporta um deck pelo nome em formato JSON.

### `GET /decks/backup`
Exporta todos os decks em formato JSON (backup completo).

**Resposta:** Arquivo JSON com todos os decks

---

## Schemas Principais

### Card
```json
{
  "_id": "string",
  "name": "string",
  "scryfall_id": "string (UUID)",
  "oracle_id": "string (UUID, opcional)",
  "mana_cost": "string (ex: '{2}{R}{R}')",
  "cmc": "number",
  "type_line": "string",
  "oracle_text": "string",
  "power": "string (opcional)",
  "toughness": "string (opcional)",
  "colors": ["string"],
  "color_identity": ["string"],
  "rarity": "string",
  "set_name": "string",
  "set_code": "string",
  "image_uris": {
    "small": "string",
    "normal": "string",
    "large": "string",
    "png": "string",
    "art_crop": "string",
    "border_crop": "string"
  },
  "prices": {
    "usd": "string",
    "usd_foil": "string",
    "eur": "string",
    "eur_foil": "string",
    "tix": "string"
  }
}
```

### Deck
```json
{
  "_id": "string",
  "name": "string (mínimo 3 caracteres)",
  "format": "string (commander, standard, modern, legacy, vintage, pauper, bulk)",
  "cards": [
    {
      "scryfall_id": "string",
      "quantity": "number (mínimo 1)"
    }
  ],
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `MONGO_USER` | Usuário do MongoDB | **Obrigatório** |
| `MONGO_PASS` | Senha do MongoDB | **Obrigatório** |
| `MONGO_DB` | Nome do banco de dados | `mtg_database` |
| `MONGO_HOST` | Host do MongoDB | `mongo` |
| `MONGO_PORT` | Porta do MongoDB | `27017` |
| `API_PORT` | Porta da API | `8000` |

---

## Comandos Úteis

### Iniciar os containers
```bash
docker-compose up -d
```

### Parar os containers
```bash
docker-compose down
```

### Ver logs da API
```bash
docker-compose logs -f api
```

### Reconstruir a API (após mudanças no Dockerfile ou requirements.txt)
```bash
cd backend
./update-api.ps1
```

### Acessar MongoDB via CLI
```bash
docker exec -it mtg_mongo mongosh -u <MONGO_USER> -p <MONGO_PASS>
```

### Acessar Mongo Express (Interface Web)
```
http://localhost:8081
```

---

## Validações e Regras

### Cartas
- `scryfall_id` é único e obrigatório
- Cartas duplicadas são atualizadas automaticamente (upsert)
- Importação em massa divide automaticamente em lotes de 75 (limite da Scryfall)

### Decks
- Nome do deck deve ter no mínimo 3 caracteres
- Nome do deck deve ser único
- Formato é obrigatório
- Quantidade de cartas deve ser no mínimo 1

### Performance
- Índices MongoDB criados automaticamente na inicialização
- Buscas otimizadas com índices em `scryfall_id`, `name`, `format`, `colors`, `rarity`
- Queries em batch para reduzir requisições ao banco

---

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Criado com sucesso |
| 204 | Sem conteúdo (deletado) |
| 400 | Requisição inválida (validação, ID inválido, etc.) |
| 404 | Recurso não encontrado |
| 500 | Erro interno do servidor |

---

## Notas Importantes

1. **Scryfall API**: A API usa a Scryfall API pública. Respeite os rate limits.
2. **Imagens**: As URLs de imagem vêm diretamente da Scryfall e podem expirar.
3. **IDs**: Todos os `_id` do MongoDB são convertidos para string nas respostas.
4. **Paginação**: Use `limit` e `skip` para paginar resultados grandes.
5. **Exportação**: Endpoints de exportação buscam nomes faltantes na Scryfall automaticamente.

---

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## Licença

Este projeto está sob a licença MIT.
