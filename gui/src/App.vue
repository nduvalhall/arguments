<template>
    <div class="container">
        <div class="activity-tabs">
            <button
                @click="currentView = 'forms'"
                :class="{ active: currentView === 'forms' }"
                class="tab-button"
            >
                Forms
            </button>
            <button
                @click="currentView = 'table'"
                :class="{ active: currentView === 'table' }"
                class="tab-button"
            >
                Activity Table
            </button>
        </div>

        <div v-if="currentView === 'forms'">
            <div class="activity-tabs">
                <button
                    @click="currentActivity = 'set-parameter'"
                    :class="{ active: currentActivity === 'set-parameter' }"
                    class="tab-button"
                >
                    Set Parameter
                </button>
                <button
                    @click="currentActivity = 'get-parameter'"
                    :class="{ active: currentActivity === 'get-parameter' }"
                    class="tab-button"
                >
                    Get Parameter
                </button>
            </div>

            <DynamicForm
                :schema="
                    currentActivity === 'set-parameter'
                        ? setParameterSchema
                        : getParameterSchema
                "
                submitButtonText="Execute"
                @submit="handleFormSubmit"
            />
        </div>

        <div v-else-if="currentView === 'table'">
            <ActivityTable @save="handleActivitiesSave" />
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import DynamicForm from "./components/DynamicForm.vue";
import ActivityTable from "./components/ActivityTable.vue";
import type { Schema } from "./types/schema";

const currentView = ref("forms");
const currentActivity = ref("set-parameter");

const setParameterSchema: Schema = {
    activity: "set-parameter",
    title: "Set Parameter",
    description: "Configure and set a parameter for the selected target",
    endpoint: "POST /set-parameter",
    arguments: [
        {
            name: "target",
            label: "Target",
            type: "list",
            dataSource: {
                type: "remote",
                url: "GET /set-parameter/targets",
            },
            default: "",
            required: true,
        },
        {
            name: "parameter",
            label: "Parameter",
            type: "list",
            dataSource: {
                type: "remote",
                url: "GET /set-parameter/parameters",
                dependencies: ["target"],
            },
            default: "",
            required: true,
        },
        {
            name: "value",
            label: "Value",
            type: "string",
            validation: [
                {
                    type: "required",
                    message: "Value is required",
                },
                {
                    type: "remote",
                    url: "POST /set-parameter/validate-value",
                    dependencies: ["target", "parameter", "value"],
                },
            ],
            default: "",
        },
        {
            name: "timeout",
            label: "Timeout (seconds)",
            type: "number",
            default: 30,
            required: false,
            validation: [
                {
                    type: "min",
                    value: 1,
                    message: "Timeout must be at least 1 second",
                },
                {
                    type: "max",
                    value: 300,
                    message: "Timeout cannot exceed 300 seconds",
                },
            ],
        },
    ],
};

const getParameterSchema: Schema = {
    activity: "get-parameter",
    title: "Get Parameter",
    description: "Retrieve a parameter value from the selected target",
    endpoint: "POST /get-parameter",
    arguments: [
        {
            name: "target",
            label: "Target",
            type: "list",
            dataSource: {
                type: "remote",
                url: "GET /get-parameter/targets",
            },
            default: "",
            required: true,
        },
        {
            name: "parameter",
            label: "Parameter",
            type: "list",
            dataSource: {
                type: "remote",
                url: "GET /get-parameter/parameters",
                dependencies: ["target"],
            },
            default: "",
            required: true,
        },
        {
            name: "timeout",
            label: "Timeout (seconds)",
            type: "number",
            default: 30,
            required: false,
            validation: [
                {
                    type: "min",
                    value: 1,
                    message: "Timeout must be at least 1 second",
                },
                {
                    type: "max",
                    value: 300,
                    message: "Timeout cannot exceed 300 seconds",
                },
            ],
        },
    ],
};

const handleFormSubmit = (formData: Record<string, any>, result: any) => {
    console.log(`${currentActivity.value} submitted:`, formData);
    console.log("Execution result:", result);
};

const handleActivitiesSave = (activities: any[]) => {
    console.log("Activities saved:", activities);
    // Here you could convert the activities to schema format
    // or send them to a server, etc.
};
</script>

<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen,
        Ubuntu, Cantarell, "Open Sans", "Helvetica Neue", sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.activity-tabs {
    display: flex;
    margin-bottom: 20px;
    border-bottom: 1px solid #e5e7eb;
}

.tab-button {
    padding: 10px 20px;
    border: none;
    background-color: transparent;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.tab-button:hover {
    background-color: #f9fafb;
}

.tab-button.active {
    color: #3b82f6;
    border-bottom: 2px solid #3b82f6;
}
</style>
