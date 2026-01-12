# Version Manager Business Logic and Flows

This document describes the business logic and workflows for the Version Manager application. Cross-references to APIs are in [apis.md](apis.md) and GUI documentation is in [gui.md](gui.md).

---

## Images

### Create Image

A new image can be created from the GUI using the **Create** button. The parameters are `name` and `domain`. The domain name is selected via a dropdown menu with existing domain names. If the domain doesn't exist, there is an option to create a new domain and associate it with the image.

Creates an entry in the `ImageDomain` table to track image → domain associations.
GUI:
- New image appears on `Images` window
- Number of versions is 0
- New version can be created only via API.

**Required APIs:**

- `POST /v1/images/create` - Create image entry in ImageDomain table ([apis.md#L81](apis.md#L81))
- `GET /v1/domains/list` - Populate domain dropdown ([apis.md#L161](apis.md#L161))
- `GET /v1/images/list` - Shows newly created image after action is completed

**GUI Windows:**

- Images - Create (+) ([gui.md#L40](gui.md#L40))

---

### Add New Image Version

Add a new image version using the `curl` API after a successful build and tests from a GitHub Actions job. The API performs the following:

1. Adds a new entry to the `Image` table with the provided version
2. Sets `tested: false`
3. Gets `domain` value from `ImageDomain.{image-name}.domain`
4. **Automatically updates the active domain** in the `dev` environment by adding or replacing this image in the domain's `images` list

**Required APIs:**

- `POST /v1/images/{image-name}/create` - Create image version and auto-update active domain ([apis.md#L97](apis.md#L97))

---

### Mark Image as Tested

Can be done from the GUI as well as using `curl` from a GitHub Actions job.
1. Sets `tested: true` or `tested: false` for the provided `{image-name}` and `version`.
2. Updates related domains, setting tested status in the image element in the `Domains.images` List.

**Required APIs:**

- `PUT /v1/images/{image-name}/tested` - Set tested status ([apis.md#L112](apis.md#L112))

**GUI Windows:**

- Image Version - Edit ([gui.md#L73](gui.md#L73))

---

### Edit and Delete Image

Can be done from the GUI. Uses the existing APIs and GUI windows.

#### Rename Image

1. Goes to related domains, updates all versions: sets new image name in `domain.images` lists
2. Updates image name for all image versions in `Image` table
3. Updates `ImageDomain.{image-name}.image` value
4. Reloads the window

**Required APIs:**

- `PUT /v1/images/{image-name}/rename` - Rename image ([apis.md#L138](apis.md#L138))

**GUI Windows:**

- Image - Edit ([gui.md#L49](gui.md#L49))

#### Change Image's Domain

1. Updates `ImageDomain.{image-name}.domain` to new domain name
2. Moves old domain name to `ImageDomain.{image-name}.domains` list if not already present
3. Adds the latest image version to new domain's `active` version in `dev` environment
4. Removes the image from old domain's `active` versions in `dev` environment.
5. Previous image versions remain associated with the old `inactive` domain's versions.
6. User can then go to the new domain and update image version using the standard procedure

**Required APIs:**

- `PUT /v1/images/{image-name}/domain` - Change domain ([apis.md#L126](apis.md#L126))

**GUI Windows:**

- Image - Edit ([gui.md#L49](gui.md#L49))


#### Delete Image

1. Get `ImageDomain.{image-name}.domains` list of all domains the image was associated with
2. For each domain, remove the image entry from all domain versions' `images` lists
3. Remove all image versions from the `Image` table
4. Delete `ImageDomain.{image-name}` entry

**Required APIs:**

- `DELETE /v1/images/{image-name}` - Delete image ([apis.md#L152](apis.md#L152))

**GUI Windows:**

- Image - Delete ([gui.md#L55](gui.md#L55))

---

## Domains

### Create Domain

Can be done from the GUI:

- From the Domains main window using `+ Add Domain` button
- From the **New Image** dropdown menu when creating an image

**Required APIs:**

- `POST /v1/domains/{domain-name}/create` - Create domain with version ([apis.md#L184](apis.md#L184))
- `GET /v1/domains/list` - Check existing domains ([apis.md#L161](apis.md#L161))

**GUI Windows:**

- Domains - Create (+) ([gui.md#L84](gui.md#L84))
- Images - Create (+) → New domain option ([gui.md#L46](gui.md#L46))

---

### Create New Domain Version

Can be done from the GUI and via API. Default values:

- `deployed: "dev"`
- `active: true`
- `version`: current date in format `YYYY-MM-DD-hh-mm-ss`

The `images` list contains all the latest created images for this domain from `dev` environment. The previous `active` version becomes `inactive`.

**Required APIs:**

- `POST /v1/domains/{domain-name}/create` - Create new version ([apis.md#L184](apis.md#L184))
- `GET /v1/domains/{domain-name}/active` - Get previous active version's images ([apis.md#L180](apis.md#L180))

**GUI Windows:**

- Domain Version - Create (+) in Specific Domain Window ([gui.md#L109](gui.md#L109))

---

### Set Domain Version as Tested

Can be done from the GUI and via API. Sets the domain version to `tested: true`.

**Requirements:**
- Domain version can only be set as tested if all images in the `domain.images` list have `tested: true`
- The "Tested" checkbox is disabled in the GUI if any image in the `images` list has `tested: false`

**Cascade behavior:** Also sets `tested: true` for all images in the `domain.images` list.

**Required APIs:**

- `PUT /v1/domains/tested` - Set domain tested status with image cascade ([apis.md#L236](apis.md#L236))

**GUI Windows:**

- Domain Version - Edit ([gui.md#L135](gui.md#L135))

---

### Set Domain Version as Active

Can be done from the GUI and via API. Sets a specific domain version as `active: true` and deactivates the previous active version for that environment.

**Validation:** Only one domain version can be active per environment. If the payload contains multiple versions for the same environment, an error is returned.

**Required APIs:**

- `PUT /v1/domains/active` - Set domain active status ([apis.md#L262](apis.md#L262))
- `GET /v1/domains/active?env=[dev|staging|prod]` - Get active domain for specific environment ([apis.md#L171](apis.md#L171))

**GUI Windows:**

- Domain Version - Edit ([gui.md#L135](gui.md#L135))

---

### Promote Domain Version

Can be done from the GUI and via API. Promotes a domain version according to the rule:

| Current Value | Promote to     |
|---------------|----------------|
| dev           | staging        |
| staging       | prod           |
| prod          | *(none)*       |

**Requirements**
- Domain can't be promoted if its own status is `tested: false` 

**Cascade behavior:**
- The promoted domain version becomes `active: true`
- The previous active domain version for that environment becomes `active: false`
- **If promoting an `active` domain version to `staging`:**
  a. Domain's `tested` status is reset to `false`
  b. A new domain version with timestamp `now` is created in the `dev` environment with `tested: false` and `active: true`

**Required APIs:**

- `PUT /v1/domains/promote` - Promote domain version with image cascade ([apis.md#L288](apis.md#L288))
- `POST /v1/domains/{domain-name}/create` - Create new domain version ([apis.md#L184](apis.md#L184))

**GUI Windows:**

- Domain Version - Edit modal → Promote dropdown ([gui.md#L135](gui.md#L135)). When promoting an active domain version to staging, a new domain version is automatically created in the dev environment with `tested: false` and `active: true`.

---

### Edit Domain Version

Can be done from the GUI and via API. Allows editing the image version for images in the `domain.images` list.

**Required APIs:**

- `PUT /v1/domains/update` - Update images in domain ([apis.md#L198](apis.md#L198))
- `GET /v1/images/{image-name}/versions` - Get available image versions for dropdown ([apis.md#L71](apis.md#L71))

**GUI Windows:**

- Domain Version - Images modal → Edit image version dropdown ([gui.md#L126](gui.md#L126))

---

### Rename Domain

Can be done from the GUI and via API.

1. Update `domain` field in all related image versions in `Image` table
2. Update `ImageDomain` table: replace `domain` value and update `domains` lists
3. Rename all domain entries in `Domain` table

**Required APIs:**

- `PUT /v1/domains/{domain-name}/rename` - Rename domain ([apis.md#L314](apis.md#L314))

**GUI Windows:**

- Domains - Edit ([gui.md#L88](gui.md#L88))

---

### Delete Domain Version

Can be done from the GUI and via API. Deletes a specific domain version.

**Required APIs:**

- `DELETE /v1/domains/{domain-name}/{version}` - Delete specific version ([apis.md#L332](apis.md#L332))

**GUI Windows:**

- Domain Version - Delete ([gui.md#L142](gui.md#L142))

---

### Delete All Domain Versions

Can be done from the GUI and via API. Deletes all versions of a domain.

**Required APIs:**

- `DELETE /v1/domains/{domain-name}` - Delete all versions ([apis.md#L338](apis.md#L338))

**GUI Windows:**

- Domain - Delete ([gui.md#L92](gui.md#L92))

---

## Database Tables Summary

| Table | Description |
|-------|-------------|
| `Image` | Stores image versions with name, version, domain, deployed status, and tested flag |
| `Domain` | Stores domain versions with name, version, deployed status, active/tested flags, and images list |
| `ImageDomain` | Tracks image → domain associations including current domain and historical domains list |

---

## Cascade Behaviors Summary

| Action | Cascade Effect |
|--------|----------------|
| **Create Image Version** | Auto-updates active domain in `dev` environment with new image version |
| **Set Domain Tested** | Sets `tested: true` for all images in `domain.images` list |
| **Promote Domain** | Promotes all images in `domain.images` list; resets `tested` if going to `staging` |
| **Delete Domain** | Removes image entries from domain's `images` lists |
| **Delete Image** | Removes image from all associated domains' `images` lists |

---

## Cross-Reference Index

### APIs by Category

**Image APIs:**
- `GET /v1/images/list` - [apis.md#L53](apis.md#L53)
- `GET /v1/images/list/versions` - [apis.md#L59](apis.md#L59)
- `GET /v1/images/list/tested?tested=[true|false]` - [apis.md#L65](apis.md#L65)
- `GET /v1/images/{image-name}/versions` - [apis.md#L71](apis.md#L71)
- `GET /v1/images/{image-name}/tested?tested=[true|false]` - [apis.md#L77](apis.md#L77)
- `POST /v1/images/create` - [apis.md#L81](apis.md#L81)
- `POST /v1/images/{image-name}/create` - [apis.md#L97](apis.md#L97)
- `PUT /v1/images/{image-name}/tested` - [apis.md#L112](apis.md#L112)
- `PUT /v1/images/{image-name}/domain` - [apis.md#L126](apis.md#L126)
- `PUT /v1/images/{image-name}/rename` - [apis.md#L138](apis.md#L138)
- `DELETE /v1/images/{image-name}` - [apis.md#L152](apis.md#L152)

**Domain APIs:**
- `GET /v1/domains/list` - [apis.md#L161](apis.md#L161)
- `GET /v1/domains/active` - [apis.md#L167](apis.md#L167)
- `GET /v1/domains/active?env=[dev|staging|prod]` - [apis.md#L171](apis.md#L171)
- `GET /v1/domains/{domain-name}` - [apis.md#L176](apis.md#L176)
- `GET /v1/domains/{domain-name}/active` - [apis.md#L180](apis.md#L180)
- `POST /v1/domains/{domain-name}/create` - [apis.md#L184](apis.md#L184)
- `PUT /v1/domains/update` - [apis.md#L198](apis.md#L198)
- `PUT /v1/domains/tested` - [apis.md#L236](apis.md#L236)
- `PUT /v1/domains/active` - [apis.md#L262](apis.md#L262)
- `PUT /v1/domains/promote` - [apis.md#L288](apis.md#L288)
- `PUT /v1/domains/{domain-name}/rename` - [apis.md#L314](apis.md#L314)
- `DELETE /v1/domains/{domain-name}/{version}` - [apis.md#L332](apis.md#L332)
- `DELETE /v1/domains/{domain-name}` - [apis.md#L338](apis.md#L338)

### GUI Windows by Category

**Images:**
- Images List - [gui.md#L32](gui.md#L32)
- Images - Create (+) - [gui.md#L40](gui.md#L40)
- Image - Edit - [gui.md#L49](gui.md#L49)
- Image - Delete - [gui.md#L55](gui.md#L55)
- Specific Image Window - [gui.md#L64](gui.md#L64)
- Image Version - Edit - [gui.md#L73](gui.md#L73)

**Domains:**
- Domains List - [gui.md#L81](gui.md#L81)
- Domains - Edit - [gui.md#L88](gui.md#L88)
- Domain - Delete - [gui.md#L92](gui.md#L92)
- Specific Domain Window - [gui.md#L99](gui.md#L99)
- Domain Version - Create (+) - [gui.md#L109](gui.md#L109)
- Domain Version - Images - [gui.md#L119](gui.md#L119)
- Domain Version - Edit - [gui.md#L135](gui.md#L135)
- Domain Version - Delete - [gui.md#L142](gui.md#L142)
