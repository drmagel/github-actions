# Version Manager UI - React-based Application

## File Structure

The UI application is split into multiple JavaScript files located in `image/src/ui/js/`:

| File | Description |
|------|-------------|
| `api.js` | API helper functions and AuthContext |
| `modals.js` | Reusable modal components (ConfirmModal, SuccessModal, FormModal, Badge) |
| `login.js` | Login page component |
| `images.js` | Images section (ImagesList, ImageVersions) |
| `domains.js` | Domains section (DomainsList, DomainVersions) |
| `app.js` | Main application component and entry point |

Cross-references to business logic are in [business-logics.md](business-logics.md) and API documentation is in [apis.md](apis.md).

---

## Login Page

- User: `admin`
- Password: from environment variable `ADMIN_PASSWORD` provided by Kubernetes secret
- Default password: `12VersionManager-=`

## Navigation

There are 2 sections in the left sidebar:
- Images
- Domains

---

## Images

**See also:** [apis.md#L53](apis.md#L53) - `GET /v1/images/list`

- Shows list of image names when `Images` section is selected
- `+` button to add a new image
- Filter textbox to find and filter images by name
- `Edit` and `Delete` icons near each image name
- Click on an image name to open the versions page

### Images - Create (+)

**See also:** [business-logics.md#L9](business-logics.md#L9) - Create Image, [apis.md#L81](apis.md#L81) - `POST /v1/images/create`

Opens a form with:

- **Name:** textbox accepting `[a-z0-9_-]` characters. Uppercase is converted to lowercase, invalid characters are ignored. If an image with this name already exists, a hint is displayed showing the domain that will be inherited.
- **Domain:** dropdown menu with existing domains to choose from. If an image with the entered name already exists, the domain field is disabled and shows the inherited domain. For new images, a domain must be selected.
- Option to create a new domain if required domain doesn't exist (only for new images)
- **[Create]** button at the bottom

### Image - Edit

**See also:** [business-logics.md#L55](business-logics.md#L55) - Edit and Delete Image, [apis.md#L126](apis.md#L126) - `PUT /v1/images/{image-name}/domain`, [apis.md#L138](apis.md#L138) - `PUT /v1/images/{image-name}/rename`

Opens a window with the ability to edit:
- Image name
- Domain name: dropdown menu with existing domain names, with option to create a new domain if required

### Image - Delete

**See also:** [business-logics.md#L90](business-logics.md#L90) - Delete Image, [apis.md#L152](apis.md#L152) - DELETE /v1/images/{image-name}

Opens a confirmation dialog:
- Message: "Do you want to delete image {image-name}?"
- **[Cancel]** - closes the window
- **[OK]** - deletes the image via API, shows success indicator (green ✓), then refreshes the images list

---

## Specific Image Window

**See also:** [apis.md#L71](apis.md#L71) - GET /v1/images/{image-name}/versions

Shows list of image versions when `Image name` is selected:
- Filter textbox to find and filter images by version or part of version string
- Filter dropdown to find and filter images by their tested status (All, Tested, Not tested)
- Both filters work together with AND logic
**There is no option to delete image version**

**Each image version line has:**
- Version string
- Domain name
- Tested status (clickable badge that toggles tested/untested status)
**There is no option to delete image version**

### Image Version - Tested Status Toggle

**See also:** [business-logics.md#L41](business-logics.md#L41) - Mark Image as Tested, [apis.md#L112](apis.md#L112) - PUT /v1/images/{image-name}/tested

- The tested status badge is clickable and toggles between "✓ Tested" and "Not tested"
- Clicking the badge immediately updates the tested status via API call
- The badge displays with appropriate styling (tested badge for tested status, default badge for not tested)
- A success message appears after successful toggle

---

## Domains

**See also:** [apis.md#L161](apis.md#L161) - GET /v1/domains/list

- Shows list of existing domain names
- `+` button to add a new domain

**See also:** [business-logics.md#L134](business-logics.md#L134) - Create Domain, [apis.md#L184](apis.md#L184) - POST /v1/domains/{domain-name}/create
- Filter textbox to find and filter domains by name
- Edit and Delete icons near each domain name

### Domains - Edit

**See also:** [business-logics.md#L248](business-logics.md#L248) - Rename Domain, [apis.md#L314](apis.md#L314) - PUT /v1/domains/{domain-name}/rename

- Ability to rename domain

### Domain - Delete

**See also:** [business-logics.md#L280](business-logics.md#L280) - Delete All Domain Versions, [apis.md#L338](apis.md#L338) - DELETE /v1/domains/{domain-name}

- Ability to delete entire domain
- Confirmation dialog to ensure user intent

---

## Specific Domain Window

**See also:** [apis.md#L176](apis.md#L176) - GET /v1/domains/{domain-name}

- `+ New Version` button to create a new domain version
- **Active** checkbox to filter active domain versions
- Dropdown menu to filter by environment: `[all | dev | staging | prod]`
  - Example: Select `dev` + `Active` to get active domain version in dev environment
  - Select `all` to see all domain versions
- Filter textbox to find and filter by version part of string
- Filter bool to find and filter by tested status
- Deployed environment, tested status, and active status columns
- Edit and Delete icons near each version

### Domain Version - Create (+)

**See also:** [business-logics.md#L153](business-logics.md#L153) - Create New Domain Version, [apis.md#L184](apis.md#L184) - POST /v1/domains/{domain-name}/create

Clicking the `+ New Version` button:

- Automatically generates a version timestamp in format `YYYY-MM-DD-hh-mm-ss`
- Creates a new domain version in `dev` environment
- Inherits the `images` list from the previous active version
- Sets the new version as `active: true`
- Deactivates the previous active version

### Domain Version - Images

**See also:** [business-logics.md#L233](business-logics.md#L233) - Edit Domain Version, [apis.md#L198](apis.md#L198) - PUT /v1/domains/update

Clicking on the `Version` link opens a modal window showing:

- Filter textbox to find and filter images by name
- List of all images associated with this domain version
- Each image displays its name and version
- Edit icon next to each image allows manually updating the image version via a dropdown menu containing all existing versions of that image
- `Promotion` button with ability to promote the domain version according to the rule:

| Current Value | Promote to |
|---------------|------------|
| dev | staging |
| staging | prod |
| prod | *(none)* - the button is grayed out and inactive |


### Domain Version - Edit

**See also:** [business-logics.md#L174](business-logics.md#L174) - Set Domain Version as Tested, [business-logics.md#L190](business-logics.md#L190) - Set Domain Version as Active, [apis.md#L236](apis.md#L236) - PUT /v1/domains/tested, [apis.md#L262](apis.md#L262) - PUT /v1/domains/active

Three options to set:
- Tested / Untested status
  - **Requirement:** All images in the domain version must be tested before the domain version can be set as tested
  - The "Tested" checkbox is disabled if any image in the `images` list has `tested: false`
  - A hint message "(all images must be tested first)" is shown when the checkbox is disabled
- Active status
- Promotion dropdown:
  - **Requirement:** Domain version must have `tested: true` before promotion is allowed
  - The promotion dropdown is disabled if the domain version's `tested` status is `false`
  - A warning message "⚠️ Cannot promote: Domain version is not tested" is shown when promotion is disabled
  - When promoting from `dev` to `staging`: tested status will be reset
  - When promoting from `staging` to `prod`: tested status will be kept
- **[Submit]** button at the bottom

### Domain Version - Delete

**See also:** [business-logics.md#L266](business-logics.md#L266) - Delete Domain Version, [apis.md#L332](apis.md#L332) - DELETE /v1/domains/{domain-name}/{version}

- Ability to delete domain version
- Confirmation dialog to ensure user intent

---

## Cross-Reference Index

### Business Logic References

**Image Operations:**
- Create Image - [business-logics.md#L9](business-logics.md#L9)
- Add New Image Version - [business-logics.md#L26](business-logics.md#L26)
- Mark Image as Tested - [business-logics.md#L41](business-logics.md#L41)
- Edit and Delete Image - [business-logics.md#L55](business-logics.md#L55)
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

### API References

**Image APIs:**
- GET /v1/images/list - [apis.md#L53](apis.md#L53)
- GET /v1/images/{image-name}/versions - [apis.md#L71](apis.md#L71)
- POST /v1/images/create - [apis.md#L81](apis.md#L81)
- POST /v1/images/{image-name}/create - [apis.md#L97](apis.md#L97)
- PUT /v1/images/{image-name}/tested - [apis.md#L112](apis.md#L112)
- PUT /v1/images/{image-name}/domain - [apis.md#L126](apis.md#L126)
- PUT /v1/images/{image-name}/rename - [apis.md#L138](apis.md#L138)
- DELETE /v1/images/{image-name} - [apis.md#L152](apis.md#L152)

**Domain APIs:**
- GET /v1/domains/list - [apis.md#L161](apis.md#L161)
- GET /v1/domains/{domain-name} - [apis.md#L176](apis.md#L176)
- POST /v1/domains/{domain-name}/create - [apis.md#L184](apis.md#L184)
- PUT /v1/domains/update - [apis.md#L198](apis.md#L198)
- PUT /v1/domains/tested - [apis.md#L236](apis.md#L236)
- PUT /v1/domains/active - [apis.md#L262](apis.md#L262)
- PUT /v1/domains/promote - [apis.md#L288](apis.md#L288)
- PUT /v1/domains/{domain-name}/rename - [apis.md#L314](apis.md#L314)
- DELETE /v1/domains/{domain-name}/{version} - [apis.md#L332](apis.md#L332)
- DELETE /v1/domains/{domain-name} - [apis.md#L338](apis.md#L338)
