<template>
    <div class="field-container">
        <!-- String input field -->
        <template v-if="arg.type === 'string'">
            <input
                type="text"
                :id="arg.name"
                :value="modelValue"
                @input="handleInput"
                class="form-input"
                :required="isRequired"
                :disabled="arg.disabled"
                :placeholder="arg.placeholder"
            />
        </template>

        <!-- Number field -->
        <template v-else-if="arg.type === 'number'">
            <input
                type="number"
                :id="arg.name"
                :value="modelValue"
                @input="handleNumberInput"
                class="form-input"
                :required="isRequired"
                :disabled="arg.disabled"
                :placeholder="arg.placeholder"
            />
        </template>

        <!-- Boolean field -->
        <template v-else-if="arg.type === 'boolean'">
            <div class="checkbox-container">
                <input
                    type="checkbox"
                    :id="arg.name"
                    :checked="!!modelValue"
                    @change="handleCheckboxChange"
                    :disabled="arg.disabled"
                />
                <label :for="arg.name" class="checkbox-label">{{
                    arg.label || arg.name
                }}</label>
            </div>
        </template>

        <!-- JSON field -->
        <template v-else-if="arg.type === 'json'">
            <textarea
                :id="arg.name"
                :value="
                    typeof modelValue === 'object'
                        ? JSON.stringify(modelValue, null, 2)
                        : modelValue
                "
                @input="handleJsonInput"
                class="form-input json-input"
                :required="isRequired"
                :disabled="arg.disabled"
                :placeholder="arg.placeholder || '{}'"
            >
            </textarea>
        </template>

        <!-- List field -->
        <template v-else-if="arg.type === 'list'">
            <select
                :id="arg.name"
                :value="modelValue"
                @change="handleSelectChange"
                class="form-input"
                :required="isRequired"
                :disabled="arg.disabled"
            >
                <option value="" disabled>
                    {{ arg.placeholder || `Select ${arg.label || arg.name}` }}
                </option>
                <option
                    v-for="option in options"
                    :key="option.value"
                    :value="option.value"
                >
                    {{ option.label }}
                </option>
            </select>
        </template>

        <!-- Autocomplete field -->
        <template v-else-if="arg.type === 'autocomplete'">
            <div class="autocomplete-container">
                <input
                    type="text"
                    :id="arg.name"
                    v-model="searchQuery"
                    @input="handleAutocompleteInput"
                    @focus="showAutocompleteOptions = true"
                    @blur="handleAutocompleteBlur"
                    class="form-input"
                    :required="isRequired"
                    :disabled="arg.disabled"
                    :placeholder="arg.placeholder"
                />
                <div
                    v-if="showAutocompleteOptions && filteredOptions.length > 0"
                    class="autocomplete-dropdown"
                >
                    <div
                        v-for="option in filteredOptions"
                        :key="option.value"
                        @mousedown="selectAutocompleteOption(option)"
                        class="autocomplete-option"
                    >
                        {{ option.label }}
                    </div>
                </div>
            </div>
        </template>

        <!-- Date field -->
        <template v-else-if="arg.type === 'date'">
            <input
                type="date"
                :id="arg.name"
                :value="modelValue"
                @input="handleInput"
                class="form-input"
                :required="isRequired"
                :disabled="arg.disabled"
            />
        </template>

        <!-- Validation error message -->
        <span v-if="validationError" class="validation-error">
            {{ validationError }}
        </span>

        <!-- Field description -->
        <span v-if="arg.description" class="field-description">
            {{ arg.description }}
        </span>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from "vue";
import type { Argument, ValidationRule } from "../types/schema";

const props = defineProps<{
    arg: Argument;
    modelValue: any;
    options?: Array<{
        label: string;
        value: any;
    }>;
    validationError?: string;
}>();

const emit = defineEmits<{
    (e: "update:modelValue", value: any): void;
    (e: "change", fieldName: string): void;
    (e: "validate", fieldName: string): void;
}>();

// For autocomplete component
const searchQuery = ref("");
const showAutocompleteOptions = ref(false);
const filteredOptions = computed(() => {
    if (!props.options) return [];
    if (!searchQuery.value) return props.options;

    return props.options.filter((option) =>
        option.label.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
});

// Check if field is required
const isRequired = computed(() => {
    if (props.arg.required !== undefined) return props.arg.required;

    // Check if there's a required validation rule
    if (props.arg.validation) {
        return props.arg.validation.some((rule) => rule.type === "required");
    }

    return false;
});

// Set up watches for model value changes
watch(
    () => props.modelValue,
    (newValue) => {
        // If we have a selected value for autocomplete, update the search query
        if (props.arg.type === "autocomplete" && newValue) {
            const selectedOption = props.options?.find(
                (opt) => opt.value === newValue
            );
            if (selectedOption) {
                searchQuery.value = selectedOption.label;
            }
        }
    },
    { immediate: true }
);

const handleSelectChange = (event: Event) => {
    const target = event.target as HTMLSelectElement;
    if (target) {
        emit("update:modelValue", target.value);
        emit("change", props.arg.name);
    }
};

const handleInput = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target) {
        emit("update:modelValue", target.value);
        runValidation();
    }
};

const handleNumberInput = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target) {
        const value = target.value === "" ? "" : Number(target.value);
        emit("update:modelValue", value);
        runValidation();
    }
};

const handleCheckboxChange = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target) {
        emit("update:modelValue", target.checked);
        emit("change", props.arg.name);
    }
};

const handleJsonInput = (event: Event) => {
    const target = event.target as HTMLTextAreaElement;
    if (target) {
        try {
            // Try to parse as JSON if it's valid
            const parsed = target.value ? JSON.parse(target.value) : null;
            emit("update:modelValue", parsed);
            runValidation();
        } catch (e) {
            // Just store the raw value if it's not valid JSON yet
            emit("update:modelValue", target.value);
        }
    }
};

const handleAutocompleteInput = (event: Event) => {
    const target = event.target as HTMLInputElement;
    if (target) {
        // We don't update the model value until an option is selected
        searchQuery.value = target.value;
        showAutocompleteOptions.value = true;
    }
};

const handleAutocompleteBlur = () => {
    // Hide dropdown after a short delay to allow click to register
    setTimeout(() => {
        showAutocompleteOptions.value = false;
    }, 200);
};

const selectAutocompleteOption = (option: { label: string; value: any }) => {
    emit("update:modelValue", option.value);
    searchQuery.value = option.label;
    showAutocompleteOptions.value = false;
    emit("change", props.arg.name);
};

const runValidation = () => {
    if (props.arg.validation && props.arg.validation.length > 0) {
        emit("validate", props.arg.name);
    }
};
</script>

<style scoped>
.field-container {
    display: flex;
    flex-direction: column;
    margin-bottom: 8px;
}

.form-input {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 0.25rem;
    font-size: 14px;
}

.json-input {
    font-family: monospace;
    min-height: 100px;
    white-space: pre;
}

.checkbox-container {
    display: flex;
    align-items: center;
}

.checkbox-label {
    margin-left: 8px;
    font-weight: normal;
}

.validation-error {
    color: #ef4444;
    font-size: 0.875rem;
    margin-top: 0.25rem;
}

.field-description {
    color: #6b7280;
    font-size: 0.75rem;
    margin-top: 0.25rem;
}

.autocomplete-container {
    position: relative;
}

.autocomplete-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    width: 100%;
    max-height: 200px;
    overflow-y: auto;
    background: white;
    border: 1px solid #ccc;
    border-top: none;
    border-radius: 0 0 4px 4px;
    z-index: 10;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.autocomplete-option {
    padding: 8px 12px;
    cursor: pointer;
}

.autocomplete-option:hover {
    background-color: #f3f4f6;
}
</style>
