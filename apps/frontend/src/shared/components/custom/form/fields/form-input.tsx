import { Controller, useFormContext } from "react-hook-form";
import { Input } from "@/shared/components/ui/input";
import {
  Field,
  FieldLabel,
  FieldDescription,
  FieldError,
} from "@/shared/components/ui/field";

interface FormInputProps {
  name: string;
  label?: string;
  description?: string;
  className?: string;
  inputClassName?: string;
  disabled?: boolean;
  placeholder?: string;
  type?: React.HTMLInputTypeAttribute;
}

export default function FormInput({
  name,
  label,
  placeholder,
  description,
  type = "text",
  className,
  inputClassName,
  disabled,
}: FormInputProps) {
  const { control } = useFormContext();
  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid} className={className}>
          <FieldLabel htmlFor={name}>{label}</FieldLabel>

          <Input
            {...field}
            id={name}
            type={type}
            aria-invalid={fieldState.invalid}
            placeholder={placeholder}
            className={inputClassName}
            disabled={disabled}
          />

          {description && <FieldDescription>{description}</FieldDescription>}

          {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
        </Field>
      )}
    />
  );
}
