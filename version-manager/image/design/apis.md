# Version Manager Application

Designed as an API server for managing application versions in a PostgreSQL database.
If the PostgreSQL database environment variable is `false`, use SQLite DB for testing.

Cross-references to business logic are in [business-logics.md](business-logics.md) and GUI documentation is in [gui.md](gui.md).

## Table Structures

### Image

```json
{
  "name": "",
  "version": "", // YYYY-MM-DD-hh-mm-ss
  "domain": "",
  "tested": bool 
}
```

### Domain

```json
{
  "name": "",
  "version": "", // YYYY-MM-DD-hh-mm-ss
  "deployed": "", // 'dev', 'staging', 'prod'
  "tested": bool,
  "active": bool,
  "images": [
    {
      "name": "",
      "version": "",
      "tested": bool
    }
  ]
}
```

### Image Domains
```json
{
  "name": "",
  "domain": "",
  "domains": []
}
```

## APIs

### Images

#### `GET /v1/images/list`

Lists all image names from the `ImageDomain` table.

**See also:** [business-logics.md](business-logics.md) - Images section

#### `GET /v1/images/list/versions`

Lists all image names with their versions and `tested` status from the `Images` table.

**See also:** [business-logics.md](business-logics.md) - Images section

#### `GET /v1/images/list/tested?tested=[true|false]`

Lists all tested image names with all versions

**See also:** [business-logics.md](business-logics.md) - Images section

### `GET /v1/images/{image-name}/versions`

Gets the image `{image-name}` with all versions and their status

**See also:** [business-logics.md](business-logics.md) - Images section, [gui.md#L74](gui.md#L74) - Specific Image Window

#### `GET /v1/images/{image-name}/tested?tested=[true|false]`

Gets tested image `{image-name}` with versions

### `POST /v1/images/create`

Create a new entry for `{image-name}` in `ImageDomain` table.

**See also:** [business-logics.md#L9](business-logics.md#L9) - Create Image, [gui.md#L44](gui.md#L44) - Images - Create (+)

Payload example:

```json
{
  "name": "",
  "domain": ""
}
```
The `domains` value is set to a List with one element from the `domain` value 

### `POST /v1/images/{image-name}/create`

Adds new image version to the `Image` table.
Default values: `"tested": false`, `"domain":  ImageDomain.image-name.domain`, `"deployed": "dev"`
**Auto-updates the active domain in `dev` environment** by adding or replacing this image in the domain's `images` list.

**See also:** [business-logics.md#L26](business-logics.md#L26) - Add New Image Version 

Payload example:
```json
{
  "version": "" // YYYY-MM-DD-hh-mm-ss
}
```

#### `PUT /v1/images/{image-name}/tested`

Set image `{image-name}` to `tested: true` or `tested: false`

**See also:** [business-logics.md#L41](business-logics.md#L41) - Mark Image as Tested, [gui.md#L91](gui.md#L91) - Image Version - Edit
Payload example:

```json
{
  "version": "",
  "tested": bool
}
```

#### `PUT /v1/images/{image-name}/domain`

Updates `domain` to `{domain-name}` in the `ImageDomain.{image-name}.domain` field. Moves `{old-domain-name}` to the `ImageDomain.{image-name}.domains` List if `{old-domain-name}` doesn't exist in the List. Adds the last created `{image-name}` version to the `{domain-name}.images` List

**See also:** [business-logics.md#L74](business-logics.md#L74) - Change Image's Domain, [gui.md#L55](gui.md#L55) - Image - Edit

```json
{
  "domain": domain-name,
}
```

#### `PUT /v1/images/{image-name}/rename`

Renames `{image-name}` to `{new-image-name}`: first updates the name in all `domain.images` lists, then renames all image entries. Updates the `ImageDomain` table, replacing the `ImageDomain.{image-name}.name` value.

**See also:** [business-logics.md#L59](business-logics.md#L59) - Rename Image, [gui.md#L55](gui.md#L55) - Image - Edit

Payload example:

```json
{
  "name": new-name,
}
```

#### `DELETE /v1/images/{image-name}`

Deletes image entries from the current domain versions' `images` Lists.
Goes through the `ImageDomain.{image-name}.domains` List and from each domain, deletes the image entry from all domain versions' `images` Lists. Then deletes all image versions and deletes the `ImageDomain.{image-name}` entry

**See also:** [business-logics.md#L90](business-logics.md#L90) - Delete Image, [gui.md#L63](gui.md#L63) - Image - Delete

### Domains

#### `GET /v1/domains/list`

Lists all domains with names, versions, status, and list of images

**See also:** [business-logics.md](business-logics.md) - Domains section, [gui.md#L100](gui.md#L100) - Domains List

#### `GET /v1/domains/active`

Lists all active domains with names, versions, image versions, and status

#### `GET /v1/domains/active?env=[dev|staging|prod]`

Lists the environment-related active domain with name, version, image versions, and status


#### `GET /v1/domains/{domain-name}`

Lists all domain entries with `{domain-name}` with version, image versions and status

#### `GET /v1/domains/{domain-name}/active`

Lists active `{domain-name}` with version, status, and image versions

#### `POST /v1/domains/{domain-name}/create`

Creates a new version of `{domain-name}` with all the related last created images. The domain version is created in the `dev` environment and automatically becomes `active: true`. The previously active version is set to `active: false`.

**See also:** [business-logics.md#L134](business-logics.md#L134) - Create Domain, [business-logics.md#L153](business-logics.md#L153) - Create New Domain Version, [gui.md#L104](gui.md#L104) - Domains - Create (+), [gui.md#L140](gui.md#L140) - Domain Version - Create (+)

Payload example:

```json
{
  "version": "" // YYYY-MM-DD-hh-mm-ss
}
```

#### `PUT /v1/domains/update`

Updates the image version in the `{domain-name}.images` List.

**See also:** [business-logics.md#L233](business-logics.md#L233) - Edit Domain Version, [gui.md#L152](gui.md#L152) - Domain Version - Images → Edit image version dropdown

Payload example:

```json
[
  {
    "name": "",
    "version": "", // YYYY-MM-DD-hh-mm-ss
    "images": [
      {
        "name": "",
        "version": ""
      }
    ]
  }
]
```

Or for one image:

```json
{
  "name": "",
  "version": "", // YYYY-MM-DD-hh-mm-ss
  "images": [
    {
      "name": "",
      "version": ""
    }
  ]
}
```

#### `PUT /v1/domains/tested`

Set domain status to tested. **Also sets `tested: true` for all images in the domain's `images` list.**

**See also:** [business-logics.md#L174](business-logics.md#L174) - Set Domain Version as Tested, [gui.md#L171](gui.md#L171) - Domain Version - Edit

Payload example:

```json
[
  {
    "name": "",
    "version": "" // YYYY-MM-DD-hh-mm-ss
  }
]
```

Or for one domain:

```json
{
  "name": "",
  "version": "" // YYYY-MM-DD-hh-mm-ss
}
```

#### `PUT /v1/domains/active`

Set domain to `active` state. Will remove `active` state from the previous version and set it to the provided.
Make sure there is only one domain per environment in the payload list, otherwise return error.

**See also:** [business-logics.md#L190](business-logics.md#L190) - Set Domain Version as Active, [gui.md#L171](gui.md#L171) - Domain Version - Edit

Payload example:

```json
[
  {
    "name": "",
    "version": "", // YYYY-MM-DD-hh-mm-ss
  }
]
```

Or for one domain:
```json
{
  "name": "",
  "version": "", // YYYY-MM-DD-hh-mm-ss
}
```

#### `PUT /v1/domains/promote`

Promotes domain version to the provided environment. The promoted domain version becomes `Active` and replaces the old `Active` version. **Also promotes all images in the domain's `images` list to the same environment, and if `"deployed": "staging"`, resets their `tested` status.**

**See also:** [business-logics.md#L207](business-logics.md#L207) - Promote Domain Version, [business-logics.md#L107](business-logics.md#L107) - Image Promotion, [gui.md#L171](gui.md#L171) - Domain Version - Edit → Promote dropdown

Payload example:

```json
[
  {
    "name": "",
    "version": "", // YYYY-MM-DD-hh-mm-ss
  }
]
```

Or for one domain:

```json
{
  "name": "",
  "version": "", // YYYY-MM-DD-hh-mm-ss
}
```

#### `PUT /v1/domains/{domain-name}/rename`

Renames `{domain-name}` to `{new-domain-name}`.
1. Updates `domain` field in all related images and its versions
- Table `Images` - updates all related image versions with new domain name
- Table  `ImageDomain` - goes through all entries, replacing `domain` value and replacing element in the `domains` List
2. Renames all domain entries.

**See also:** [business-logics.md#L248](business-logics.md#L248) - Rename Domain, [gui.md#L111](gui.md#L111) - Domains - Edit

Payload example:

```json
{
  "name": ""
}
```

#### DELETE /v1/domains/{domain-name}/{version}

Deletes specific `{domain-name}` version

**See also:** [business-logics.md#L266](business-logics.md#L266) - Delete Domain Version, [gui.md#L180](gui.md#L180) - Domain Version - Delete

#### DELETE /v1/domains/{domain-name} - delete all `{domain-name}` versions

1. Make sure the domain exists
2. Make sure the domain has no images in ImageDomain table
3. Delete all domain versions

**See also:** [business-logics.md#L280](business-logics.md#L280) - Delete All Domain Versions, [gui.md#L117](gui.md#L117) - Domain - Delete

## GUI

- GET / - serve the React UI application (static files)

---

## Cross-Reference Index

### Business Logic References

**Image Operations:**
- Create Image - [business-logics.md#L9](business-logics.md#L9)
- Add New Image Version - [business-logics.md#L26](business-logics.md#L26)
- Mark Image as Tested - [business-logics.md#L41](business-logics.md#L41)
- Rename Image - [business-logics.md#L59](business-logics.md#L59)
- Change Image's Domain - [business-logics.md#L74](business-logics.md#L74)
- Delete Image - [business-logics.md#L90](business-logics.md#L90)
- Image Promotion - [business-logics.md#L107](business-logics.md#L107)

**Domain Operations:**
- Create Domain - [business-logics.md#L134](business-logics.md#L134)
- Create New Domain Version - [business-logics.md#L153](business-logics.md#L153)
- Set Domain Version as Tested - [business-logics.md#L174](business-logics.md#L174)
- Set Domain Version as Active - [business-logics.md#L190](business-logics.md#L190)
- Promote Domain Version - [business-logics.md#L207](business-logics.md#L207)
- Edit Domain Version - [business-logics.md#L233](business-logics.md#L233)
- Rename Domain - [business-logics.md#L248](business-logics.md#L248)
- Delete Domain Version - [business-logics.md#L266](business-logics.md#L266)
- Delete All Domain Versions - [business-logics.md#L280](business-logics.md#L280)

### GUI References

**Images:**
- Images List - [gui.md#L32](gui.md#L32)
- Images - Create (+) - [gui.md#L40](gui.md#L40)
- Image - Edit - [gui.md#L49](gui.md#L49)
- Image - Delete - [gui.md#L55](gui.md#L55)
- Specific Image Window - [gui.md#L64](gui.md#L64)
- Image Version - Edit - [gui.md#L73](gui.md#L73)

**Domains:**
- Domains List - [gui.md#L81](gui.md#L81)
- Domains - Create (+) - [gui.md#L84](gui.md#L84)
- Domains - Edit - [gui.md#L88](gui.md#L88)
- Domain - Delete - [gui.md#L92](gui.md#L92)
- Specific Domain Window - [gui.md#L99](gui.md#L99)
- Domain Version - Create (+) - [gui.md#L109](gui.md#L109)
- Domain Version - Images - [gui.md#L119](gui.md#L119)
- Domain Version - Edit - [gui.md#L135](gui.md#L135)
- Domain Version - Delete - [gui.md#L142](gui.md#L142)
