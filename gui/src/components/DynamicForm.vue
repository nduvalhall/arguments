<template>
    <div class="form-container">
        <h2 v-if="schema.title" class="form-title">{{ schema.title }}</h2>
        <p v-if="schema.description" class="form-description">
            {{ schema.description }}
        </p>

        <div
            v-for="arg in schema.arguments"
            :key="arg.name"
            class="form-group"
            v-show="!isFieldHidden(arg)"
        >
            <label :for="arg.name" class="form-label">
                {{ arg.label || arg.name }}
                <span v-if="isFieldRequired(arg)" class="required-indicator"
                    >*</span
                >
            </label>

            <FormField
                :arg="arg"
                v-model="form[arg.name]"
                :options="options[arg.name]"
                :validation-error="validationErrors[arg.name]"
                @change="onFieldChange"
                @validate="validateField"
            />
        </div>

        <button
            @click="handleSubmit"
            class="submit-button"
            :disabled="!isFormValid"
        >
            {{ submitButtonText || "Submit" }}
        </button>
    </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted, watch } from "vue";
import FormField from "./FormField.vue";
import type { Schema, Argument, ValidationRule } from "../types/schema";

const props = defineProps<{
    schema: Schema;
    baseUrl?: string;
    submitButtonText?: string;
}>();

const emit = defineEmits<{
    (e: "submit", formData: Record<string, any>, result: any): void;
}>();

const BASE_URL = props.baseUrl || "http://localhost:8000";
const form = reactive<Record<string, any>>({});
const options = reactive<Record<string, any[]>>({});
const validationErrors = reactive<Record<string, string>>({});
const isFormValid = ref(false);

// Field visibility handling
const isFieldHidden = (arg: Argument): boolean => {
    if (arg.hidden) return true;

    // Check if field depends on other field values
    if (arg.dependsOn && arg.dependsOn.length > 0) {
        return !arg.dependsOn.every((dependency) => {
            return form[dependency.field] === dependency.value;
        });
    }

    return false;
};

// Field requirement handling
const isFieldRequired = (arg: Argument): boolean => {
    if (arg.required !== undefined) return arg.required;

    // Check if there's a required validation rule
    if (arg.validation) {
        return arg.validation.some((rule) => rule.type === "required");
    }

    return false;
};

const validateForm = () => {
    // Check for any validation errors
    if (Object.values(validationErrors).some((error) => error !== "")) {
        isFormValid.value = false;
        return;
    }

    // Check if all required fields have values
    for (const arg of props.schema.arguments) {
        // Skip validation for hidden fields
        if (isFieldHidden(arg)) continue;

        // Check required fields
        if (
            isFieldRequired(arg) &&
            (form[arg.name] === undefined || form[arg.name] === "")
        ) {
            isFormValid.value = false;
            return;
        }
    }

    isFormValid.value = true;
};

const validateField = async (fieldName: string) => {
    const arg = props.schema.arguments.find((a) => a.name === fieldName);

    if (!arg || !arg.validation) return true;

    // Clear existing validation error
    validationErrors[fieldName] = "";

    // Run through each validation rule
    for (const rule of arg.validation) {
        // Skip validation for hidden fields
        if (isFieldHidden(arg)) continue;

        const value = form[fieldName];

        // Check built-in validation rules
        if (rule.type === "required" && (value === undefined || value === "")) {
            validationErrors[fieldName] =
                rule.message || `${arg.label || arg.name} is required`;
            validateForm();
            return false;
        }

        if (
            rule.type === "min" &&
            typeof value === "number" &&
            value < rule.value
        ) {
            validationErrors[fieldName] =
                rule.message || `Minimum value is ${rule.value}`;
            validateForm();
            return false;
        }

        if (
            rule.type === "max" &&
            typeof value === "number" &&
            value > rule.value
        ) {
            validationErrors[fieldName] =
                rule.message || `Maximum value is ${rule.value}`;
            validateForm();
            return false;
        }

        if (
            rule.type === "minLength" &&
            typeof value === "string" &&
            value.length < rule.value
        ) {
            validationErrors[fieldName] =
                rule.message || `Minimum length is ${rule.value} characters`;
            validateForm();
            return false;
        }

        if (
            rule.type === "maxLength" &&
            typeof value === "string" &&
            value.length > rule.value
        ) {
            validationErrors[fieldName] =
                rule.message || `Maximum length is ${rule.value} characters`;
            validateForm();
            return false;
        }

        if (
            rule.type === "pattern" &&
            typeof value === "string" &&
            !new RegExp(rule.value).test(value)
        ) {
            validationErrors[fieldName] = rule.message || `Invalid format`;
            validateForm();
            return false;
        }

        // Remote validation
        if (rule.type === "remote" && rule.url) {
            try {
                const url =
                    BASE_URL + rule.url.replace(/^(GET|POST|PUT|DELETE) /, "");

                const data: Record<string, any> = { [fieldName]: value };

                // Add dependencies if defined
                if (rule.dependencies) {
                    for (const dep of rule.dependencies) {
                        data[dep] = form[dep];
                    }
                }

                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(data),
                });

                if (!response.ok) {
                    validationErrors[fieldName] =
                        "Server error during validation";
                    validateForm();
                    return false;
                }

                const result = await response.json();

                if (result === null) {
                    // Validation passed
                } else {
                    validationErrors[fieldName] =
                        typeof result === "string" ? result : "Invalid value";
                    validateForm();
                    return false;
                }
            } catch (error) {
                console.error(`Validation failed for ${fieldName}`, error);
                validationErrors[fieldName] = "Validation failed";
                validateForm();
                return false;
            }
        }
    }

    // All validation rules passed
    validateForm();
    return true;
};

const loadOptions = async (arg: Argument) => {
    const dataSource = arg.dataSource;
    if (!dataSource) return;

    // Handle static data
    if (dataSource.type === "static" && dataSource.data) {
        options[arg.name] = dataSource.data.map((item: any) => {
            if (typeof item === "object") {
                const label = dataSource.labelKey
                    ? item[dataSource.labelKey]
                    : item.label;
                const value = dataSource.valueKey
                    ? item[dataSource.valueKey]
                    : item.value;
                return { label, value };
            } else {
                return { label: String(item), value: item };
            }
        });
        return;
    }

    // Handle remote data
    if (dataSource.type === "remote" && dataSource.url) {
        let url =
            BASE_URL + dataSource.url.replace(/^(GET|POST|PUT|DELETE) /, "");

        // Add dependencies as query parameters
        if (dataSource.dependencies && dataSource.dependencies.length > 0) {
            const params = new URLSearchParams();
            for (const dep of dataSource.dependencies) {
                if (form[dep]) {
                    params.append(dep, form[dep]);
                }
            }
            url += `?${params.toString()}`;
        }

        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const res = await response.json();

            // Map response to options format
            options[arg.name] = res.map((item: any) => {
                if (typeof item === "object") {
                    const label = dataSource.labelKey
                        ? item[dataSource.labelKey]
                        : item.label;
                    const value = dataSource.valueKey
                        ? item[dataSource.valueKey]
                        : item.value;
                    return { label, value };
                } else {
                    return { label: String(item), value: item };
                }
            });
        } catch (error) {
            console.error(`Failed loading options for ${arg.name}`, error);
            options[arg.name] = [];
        }
    }
};

const onFieldChange = (fieldName: string) => {
    // Clear validation errors for this field
    validationErrors[fieldName] = "";

    // Reload options for fields that depend on this one
    for (const arg of props.schema.arguments) {
        if (arg.dataSource?.dependencies?.includes(fieldName)) {
            // Reset value of dependent field
            form[arg.name] = arg.default;
            loadOptions(arg);
        }

        // Clear validation errors for fields with validation that depends on this one
        if (arg.validation) {
            for (const rule of arg.validation) {
                if (rule.dependencies?.includes(fieldName)) {
                    validationErrors[arg.name] = "";
                }
            }
        }
    }

    validateForm();
};

const handleSubmit = async () => {
    // Validate all fields first
    let isValid = true;

    for (const arg of props.schema.arguments) {
        // Skip validation for hidden fields
        if (isFieldHidden(arg)) continue;

        // Check required fields
        if (
            isFieldRequired(arg) &&
            (form[arg.name] === undefined || form[arg.name] === "")
        ) {
            validationErrors[arg.name] = `${arg.label || arg.name} is required`;
            isValid = false;
        }

        // Run all validation rules
        if (arg.validation && arg.validation.length > 0) {
            const valid = await validateField(arg.name);
            if (!valid) isValid = false;
        }
    }

    if (!isValid) {
        validateForm();
        return;
    }

    // Extract endpoint and method
    const endpoint = props.schema.endpoint.replace(
        /^(GET|POST|PUT|DELETE) /,
        ""
    );
    const method =
        props.schema.method ||
        (props.schema.endpoint.includes(" ")
            ? props.schema.endpoint.split(" ")[0]
            : "POST");

    try {
        const response = await fetch(BASE_URL + endpoint, {
            method,
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(form),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        emit("submit", form, result);
    } catch (error) {
        console.error("Submission error:", error);
    }
};

onMounted(async () => {
    // Initialize form values with defaults
    for (const arg of props.schema.arguments) {
        form[arg.name] = arg.default;

        // Load options for fields with data sources that don't depend on other fields
        if (
            arg.dataSource &&
            (!arg.dataSource.dependencies ||
                arg.dataSource.dependencies.length === 0)
        ) {
            await loadOptions(arg);
        }
    }

    validateForm();
});

// Watch for schema changes
watch(
    () => props.schema,
    async () => {
        // Reset form with new defaults
        for (const arg of props.schema.arguments) {
            form[arg.name] = arg.default;

            // Load options for fields with data sources that don't depend on other fields
            if (
                arg.dataSource &&
                (!arg.dataSource.dependencies ||
                    arg.dataSource.dependencies.length === 0)
            ) {
                await loadOptions(arg);
            }
        }

        validateForm();
    },
    { deep: true }
);
</script>

<style scoped>
.form-container {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.form-description {
    color: #6b7280;
    margin-bottom: 1rem;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-label {
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.required-indicator {
    color: #ef4444;
    margin-left: 2px;
}

.submit-button {
    padding: 0.5rem 1rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
    margin-top: 1rem;
}

.submit-button:hover {
    background-color: #2563eb;
}

.submit-button:disabled {
    background-color: #9ca3af;
    cursor: not-allowed;
}
</style>
