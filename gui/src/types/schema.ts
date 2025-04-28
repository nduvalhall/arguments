export type InputType = 
  | 'string' 
  | 'number' 
  | 'boolean'
  | 'json'
  | 'list'
  | 'autocomplete'
  | 'date'
  | 'datetime'
  | 'time';

export interface ValidationRule {
  type: 'required' | 'min' | 'max' | 'minLength' | 'maxLength' | 'pattern' | 'custom' | 'remote';
  value?: any;
  message?: string;
  url?: string;
  dependencies?: string[];
}

export interface DataSource {
  type: 'static' | 'remote' | 'callback';
  data?: any[];
  url?: string;
  dependencies?: string[];
  searchParam?: string; // For autocomplete, the query parameter name
  labelKey?: string;    // Property to use as label from returned objects
  valueKey?: string;    // Property to use as value from returned objects
}

export interface Argument {
  name: string;
  label?: string;
  type: InputType;
  default: any;
  required?: boolean;
  disabled?: boolean;
  hidden?: boolean;
  placeholder?: string;
  description?: string;
  dataSource?: DataSource;
  validation?: ValidationRule[];
  dependsOn?: {
    field: string;
    value: any;
  }[];
}

export interface Schema {
  title?: string;
  description?: string;
  activity: string;
  endpoint: string;
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  arguments: Argument[];
} 