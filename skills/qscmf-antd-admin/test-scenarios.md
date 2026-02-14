# Test Scenarios for qscmf-antd-admin Skill

## Baseline Scenarios (RED Phase)

These scenarios test what developers do WITHOUT the skill.

### Scenario 1: Basic Table Creation
**Context**: Developer needs to create a simple table with columns
**Prompt**: "Create a table component for displaying product list with id, name, price, and created_at fields"

**Expected Struggles**:
- Container pattern syntax (function vs closure)
- Which column type to use for each field
- How to set data source
- Where to call render()

**Baseline Behavior** (without skill):
- May try to instantiate columns directly instead of using container
- May use wrong column types (e.g., text for price instead of digit)
- May forget to call render()
- May not know about fluent interface

### Scenario 2: Table with Actions
**Context**: Developer needs to add CRUD operations to a table
**Prompt**: "Add edit, delete, and add new actions to the product table"

**Expected Struggles**:
- Confusion between table actions (top) vs row actions (per row)
- How to use shortcuts (addNew(), delete()) vs manual setup
- Modal integration for edit
- Permission node setup

**Baseline Behavior** (without skill):
- May add actions in wrong place (columns vs actions)
- May not discover shortcut methods
- May struggle with modal-form integration

### Scenario 3: Form with Validation
**Context**: Developer needs to create a form with validation
**Prompt**: "Create a form for adding products with required title, price, and optional description"

**Expected Struggles**:
- Form column types vs Table column types
- How to add validation rules
- Form submission setup
- Initial values setting

**Baseline Behavior** (without skill):
- May use Table column types in Form
- May not know how to add validation
- May forget to set submit request

### Scenario 4: Complex Field Types
**Context**: Developer needs to use special field types
**Prompt**: "Add an image upload field with crop and a select field for category"

**Expected Struggles**:
- Not knowing which field types exist (Image, Select, etc.)
- How to configure upload request
- How to set options for select
- Crop ratio configuration

**Baseline Behavior** (without skill):
- May use generic text field
- May not discover setValueEnum() for select
- May not know about setCrop() for images
- May struggle with upload configuration

### Scenario 5: Modal Integration
**Context**: Developer needs to open a form in a modal
**Prompt**: "Open the product add form in a modal when clicking add button"

**Expected Struggles**:
- How to create Modal component
- setContent vs setUrl
- Button->modal() integration
- Modal with Form vs Table

**Baseline Behavior** (without skill):
- May try to create modal from scratch
- May not understand setContent vs setUrl difference
- May struggle with button-modal binding

### Scenario 6: Search and Filtering
**Context**: Developer needs to customize search behavior
**Prompt**: "Disable search for ID field and enable date range search for created_at"

**Expected Struggles**:
- setSearch(false) method
- Date range field type
- Which columns support search by default

**Baseline Behavior** (without skill):
- May not find setSearch() method
- May use wrong date type
- May assume all fields are searchable

### Scenario 7: Editable Table
**Context**: Developer needs inline editing
**Prompt**: "Make the sort field in the table editable inline"

**Expected Struggles**:
- editable() method on columns
- defaultEditMode() on table
- saveRequest() on actions
- Difference between inline edit vs modal edit

**Baseline Behavior** (without skill):
- May not discover editable() method
- May not understand defaultEditMode()
- May implement custom edit instead

## Application Scenarios (GREEN Phase)

After skill is written, verify agents can:

1. **Quickly find** the right column type for a field
2. **Correctly apply** container pattern syntax
3. **Properly configure** actions and operations
4. **Successfully integrate** modals with forms
5. **Accurately set up** validation and submission
6. **Efficiently customize** search and filtering

## Gap Testing

Common use cases that must be covered:
- [ ] All 20+ column types documented with examples
- [ ] Table vs Form column differences
- [ ] Action shortcuts (addNew, delete, forbid, resume)
- [ ] Modal with Form/Table/URL
- [ ] Permission nodes
- [ ] Search configuration
- [ ] Inline editing
- [ ] Data source binding
- [ ] Form validation
- [ ] File/Image upload configuration
