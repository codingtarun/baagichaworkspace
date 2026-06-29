## Goal
- Build the complete VarietyStrain admin panel with 7-tab progressive-locked form, strain data inheritance from variety, and hierarchical tree index.

## Constraints & Preferences
- Existing Variety and Strain modules untouched
- Full boot logic on VarietyStrain model (slug gen, cascade delete/restore)
- Nested attach/detach pivot routes (rootstocks, diseases, pollinizers) + 3 PUT pivot update routes for inline editing
- Admin routes use URI `variety-strains` and name prefix `admin.variety-strains.*`
- Each migration section gets its own tab; child strain creation replicates all parent fields except name/slug
- Forms have progressive tab locking: tabs 2–7 disabled until current tab's required fields pass JS validation
- Tab order: 1 Basic Info, 2 Strains, 3 Classification & Climate, 4 Fruit & Harvest, 5 Yield & Market, 6 Media & SEO, 7 Relationships (last)
- Relationships last because user should have data before adding pivot relationships
- Slug auto-generated from name_en via JS (readonly)
- Trashed items on separate page (not inline)

## Progress
### Done
- Created fresh `Modules/VarietyStrain/` with `module:make`
- Built **4 migrations**: `variety_strains` (main), `variety_strain_rootstock`, `variety_strain_disease`, `variety_strain_pollen_variety`
  - Fixed FK name length bug on `variety_strain_pollen_variety` (MySQL 64-char limit) — used explicit short names `vs_pollen_vs_id_fk`, `vs_pollen_pollinator_id_fk`, `vs_pollen_unique`
  - All 4 migrations pass clean
- Built **4 models**: `VarietyStrain`, `VarietyStrainRootstock`, `VarietyStrainDisease`, `VarietyStrainPollenVariety`
- Updated **3 external models**: `Fruit` (hasMany), `Rootstock` (belongsToMany), `Disease` (belongsToMany)
- Created **routes/admin.php** — 22 routes (CRUD + soft-delete + toggles + media + pivot attach/detach/update + trashed)
- Created **2 form requests**: `StoreVarietyStrainRequest`, `UpdateVarietyStrainRequest` — added `strains.*.name_en`/`name_hi` validation to Store request
- Created **Admin controller**: `VarietyStrainController` with 21 methods
- Created **13 view files**: `index.blade.php` (hierarchical tree), `trashed.blade.php`, `create.blade.php`, `edit.blade.php`, `show.blade.php` (7-tab read-only), `_form.blade.php` (7-tab wrapper + Next/Prev nav + progressive lock JS + hash nav + first-invalid scrolling), 6 tab partials + `_form_tab7_strains.blade.php` (repeater in create, table in edit)
- Updated admin sidebar — added "Variety/Strain Manager" link

### View file details (latest state)
- **`_form.blade.php`** — 7-tab nav with Bootstrap nav-tabs; progressive locking (tabs 2–7 disabled in create mode); Next/Prev buttons on each tab pane; JS validation for required fields (name_en on tab 1, strain rows on tab 2); tab unlock on Next; `switchTab`/`prevTab` handlers; hash-based nav; auto-scroll to invalid field on page load; Submit button on tab 7
- **`_form_tab1_basic.blade.php`** — fruit_id with hidden for strains, parent_id select/hidden, name_en with `#input_name_en` id, slug with `#input_slug` (readonly, grey bg), sort, toggles, description; slug auto-generated from name_en via `input` event listener (only when empty or auto)
- **`create.blade.php`** — minimalist: just form with errors alert + `_form` include (`isEdit => false`); no duplicate submit buttons or JS
- **`edit.blade.php`** — form with `_form` include (`isEdit => true`); has bottom Update/View/Cancel buttons; no duplicate JS
- **`show.blade.php`** — 7 read-only tabs matching form order (Basic Info, Strains, Classification & Climate, Fruit & Harvest, Yield & Market, Media & SEO, Relationships); Strains tab shows children badges; Relationships tab shows rootstock/disease/pollinizer badges only

### In Progress
- (none)

### Blocked
- (none)

## Key Decisions
- Progressive tab locking: tabs 2–7 start disabled; only "Next" validates required fields and unlocks the next tab; "Previous" goes back freely; tab click on disabled tab blocked with a toast
- Tab 1 (Basic Info) validates `name_en` as the only required field; Tab 2 (Strains) validates each row's `name_en` if rows exist; tabs 3–7 have no strictly required fields
- `replicate()` used in `store()` to copy all parent fillable attributes to child strains — only `name_en`, `name_hi`, `slug`, `parent_id`, `view_count` differ
- In edit mode, all tabs unlocked immediately (data already exists); parent_id field hidden when editing a child strain
- Slug auto-generated from `name_en` input using JS; slug field is `readonly`

## Next Steps
- (none — panel fully built)

## Critical Context
- All 4 migrations pass clean after FK name fix
- Admin views follow pattern: `layouts.admin.app` → sections `title`, `page-title`, `breadcrumb`, `page-actions`, `content`
- Bootstrap 5 classes with custom inline styles (rounded-3, border-radius:10px)
- Booleans as `form-switch` toggles; enums as `select` dropdowns
- Media via Spatie Media Library (`featured_image` singleFile + `gallery` multiple)
- Pivot relationships use inline-editable table rows + attach modals (rootstocks: tree_vigor, growth_habit, bearing_age_years, fruit_size, yield; diseases: severity, notes; pollinizers: compatibility_rating)
- JS for create mode is in `_form.blade.php` (progressive locking + next/prev + hash nav + first-invalid scroll); slug auto-gen is in `_form_tab1_basic.blade.php`

## Relevant Files
- `Modules/VarietyStrain/routes/admin.php`: 22 admin routes
- `Modules/VarietyStrain/app/Http/Controllers/Admin/VarietyStrainController.php`: 21 methods
- `Modules/VarietyStrain/app/Http/Requests/StoreVarietyStrainRequest.php`: validation + strains array rules
- `Modules/VarietyStrain/app/Http/Requests/UpdateVarietyStrainRequest.php`: validation with ignore for unique
- `Modules/VarietyStrain/app/Models/VarietyStrain.php`: model with all relationships, scopes, boot logic
- `Modules/VarietyStrain/resources/views/admin/variety-strains/`: 13 view files
- `Modules/Core/resources/views/layouts/admin/_partials/_sidebar.blade.php`: sidebar link
