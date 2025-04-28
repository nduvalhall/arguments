<template>
    <div class="activity-table-container">
        <h2>Activities Configuration</h2>

        <table class="activity-table">
            <thead>
                <tr>
                    <th width="30%">Activity</th>
                    <th width="60%">Arguments</th>
                    <th width="10%">Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(activity, index) in activities" :key="index">
                    <td>
                        <input
                            type="text"
                            v-model="activity.name"
                            class="activity-input"
                            placeholder="Activity name"
                        />
                    </td>
                    <td>
                        <div class="arguments-container">
                            <div
                                v-for="(arg, argIndex) in activity.arguments"
                                :key="argIndex"
                                class="argument-row"
                            >
                                <input
                                    type="text"
                                    v-model="arg.name"
                                    class="argument-input"
                                    placeholder="Argument name"
                                />
                                <select
                                    v-model="arg.type"
                                    class="argument-type"
                                >
                                    <option value="">Select type</option>
                                    <option value="string">String</option>
                                    <option value="number">Number</option>
                                    <option value="boolean">Boolean</option>
                                    <option value="list">List</option>
                                    <option value="json">JSON</option>
                                </select>
                                <label class="required-checkbox">
                                    <input
                                        type="checkbox"
                                        v-model="arg.required"
                                    />
                                    Required
                                </label>
                                <button
                                    @click="removeArgument(activity, argIndex)"
                                    class="remove-btn"
                                >
                                    ✕
                                </button>
                            </div>
                            <button
                                @click="addArgument(activity)"
                                class="add-argument-btn"
                            >
                                + Add Argument
                            </button>
                        </div>
                    </td>
                    <td>
                        <button
                            @click="removeActivity(index)"
                            class="remove-btn"
                        >
                            Delete
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>

        <div class="table-actions">
            <button @click="addActivity" class="add-activity-btn">
                + Add Activity
            </button>
            <button @click="saveActivities" class="save-btn">
                Save Activities
            </button>
        </div>

        <div v-if="showPreview" class="preview-section">
            <h3>Preview</h3>
            <pre>{{ JSON.stringify(activities, null, 2) }}</pre>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, defineEmits } from "vue";
import type { InputType } from "../types/schema";

interface ActivityArgument {
    name: string;
    type: InputType | "";
    required: boolean;
    default?: any;
}

interface Activity {
    name: string;
    arguments: ActivityArgument[];
}

const emit = defineEmits<{
    (e: "save", activities: Activity[]): void;
}>();

const activities = ref<Activity[]>([
    {
        name: "",
        arguments: [],
    },
]);

const showPreview = ref(true);

const addActivity = () => {
    activities.value.push({
        name: "",
        arguments: [],
    });
};

const removeActivity = (index: number) => {
    activities.value.splice(index, 1);

    // Always keep at least one activity
    if (activities.value.length === 0) {
        addActivity();
    }
};

const addArgument = (activity: Activity) => {
    activity.arguments.push({
        name: "",
        type: "",
        required: false,
    });
};

const removeArgument = (activity: Activity, argIndex: number) => {
    activity.arguments.splice(argIndex, 1);
};

const saveActivities = () => {
    // Validate activities before saving
    const valid = activities.value.every((activity) => {
        if (!activity.name.trim()) return false;

        return activity.arguments.every(
            (arg) => arg.name.trim() !== "" && arg.type !== ""
        );
    });

    if (!valid) {
        alert("Please fill in all activity and argument fields before saving.");
        return;
    }

    emit("save", JSON.parse(JSON.stringify(activities.value)));
};
</script>

<style scoped>
.activity-table-container {
    margin-top: 20px;
}

.activity-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}

.activity-table th,
.activity-table td {
    border: 1px solid #e5e7eb;
    padding: 12px;
    text-align: left;
    vertical-align: top;
}

.activity-table th {
    background-color: #f9fafb;
    font-weight: 600;
}

.activity-input {
    width: 100%;
    padding: 8px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
}

.arguments-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.argument-row {
    display: flex;
    align-items: center;
    gap: 8px;
}

.argument-input {
    flex: 2;
    padding: 8px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
}

.argument-type {
    flex: 1;
    padding: 8px;
    border: 1px solid #d1d5db;
    border-radius: 4px;
}

.required-checkbox {
    display: flex;
    align-items: center;
    gap: 4px;
    white-space: nowrap;
}

.add-argument-btn {
    margin-top: 8px;
    background-color: transparent;
    color: #4b5563;
    border: 1px dashed #d1d5db;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.add-argument-btn:hover {
    background-color: #f9fafb;
}

.table-actions {
    display: flex;
    gap: 12px;
    margin-top: 16px;
}

.add-activity-btn {
    background-color: white;
    color: #4b5563;
    border: 1px solid #d1d5db;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.add-activity-btn:hover {
    background-color: #f9fafb;
}

.save-btn {
    background-color: #3b82f6;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.save-btn:hover {
    background-color: #2563eb;
}

.remove-btn {
    background-color: #ef4444;
    color: white;
    border: none;
    padding: 4px 8px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 12px;
}

.remove-btn:hover {
    background-color: #dc2626;
}

.preview-section {
    margin-top: 20px;
    padding: 12px;
    background-color: #f9fafb;
    border-radius: 4px;
}

.preview-section pre {
    white-space: pre-wrap;
    overflow-x: auto;
    padding: 12px;
    background-color: #f3f4f6;
    border-radius: 4px;
    font-family: monospace;
}
</style>
