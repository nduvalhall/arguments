<template>
    <div class="form-container">
        <div
            v-for="arg in schema.arguments"
            :key="arg.argument"
            class="form-group"
        >
            <label :for="arg.argument" class="form-label">
                {{ arg.argument }}
            </label>
            <template v-if="arg.type === 'list'">
                <select
                    v-model="form[arg.argument]"
                    :id="arg.argument"
                    @change="onDependencyChange(arg.argument)"
                    class="form-input"
                >
                    <option value="" disabled>Select {{ arg.argument }}</option>
                    <option
                        v-for="option in options[arg.argument]"
                        :key="option.value"
                        :value="option.value"
                    >
                        {{ option.label }}
                    </option>
                </select>
            </template>
            <template v-else-if="arg.type === 'number'">
                <input
                    type="number"
                    v-model.number="form[arg.argument]"
                    :id="arg.argument"
                    class="form-input"
                />
            </template>
        </div>

        <button @click="submit" class="submit-button">Execute</button>
    </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from "vue";

const BASE_URL = "http://localhost:8000";

interface Lookup {
    url: string;
    dependencies?: string[];
}

interface ArgumentSchema {
    argument: string;
    type: "list" | "number";
    lookup?: Lookup;
    default: string | number;
}

interface Schema {
    activity: string;
    arguments: ArgumentSchema[];
}

interface Option {
    label: string;
    value: string;
}

const schema: Schema = {
    activity: "get-parameter",
    arguments: [
        {
            argument: "target",
            type: "list",
            lookup: {
                url: "/get-parameter/targets",
            },
            default: "",
        },
        {
            argument: "parameter",
            type: "list",
            lookup: {
                url: "/get-parameter/parameters",
                dependencies: ["target"],
            },
            default: "",
        },
        {
            argument: "timeout",
            type: "number",
            default: 30,
        },
    ],
};

const form = reactive<Record<string, any>>({});
const options = reactive<Record<string, Option[]>>({});

const loadOptions = async (arg: ArgumentSchema) => {
    const lookup = arg.lookup;
    if (!lookup) return;

    let url = BASE_URL + lookup.url;

    if (lookup.dependencies) {
        const params = new URLSearchParams();
        for (const dep of lookup.dependencies) {
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
        options[arg.argument] = res.map((value: any) => ({
            label: value,
            value,
        }));
    } catch (error) {
        console.error(`Failed loading options for ${arg.argument}`, error);
        options[arg.argument] = [];
    }
};

const onDependencyChange = (changedArg: string) => {
    for (const arg of schema.arguments) {
        if (arg.lookup?.dependencies?.includes(changedArg)) {
            form[arg.argument] = "";
            loadOptions(arg);
        }
    }
};

const submit = async () => {
    const response = await fetch(BASE_URL + "/" + schema.activity, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log("Execution result:", result);
};

onMounted(async () => {
    for (const arg of schema.arguments) {
        form[arg.argument] = arg.default;
        if (arg.type === "list" && !arg.lookup?.dependencies) {
            await loadOptions(arg);
        }
    }
});
</script>

<style>
.form-container {
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-label {
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.form-input {
    padding: 0.5rem;
    border: 1px solid #ccc;
    border-radius: 0.25rem;
}

.submit-button {
    padding: 0.5rem 1rem;
    background-color: #3b82f6;
    color: white;
    border: none;
    border-radius: 0.25rem;
    cursor: pointer;
}

.submit-button:hover {
    background-color: #2563eb;
}
</style>
