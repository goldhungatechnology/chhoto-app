import { useState } from "react";
import { Controller, useFormContext } from "react-hook-form";
import { Eye, EyeOff } from "lucide-react";
import { Input } from "@/shared/components/ui/input";
import {
  Field,
  FieldLabel,
  FieldDescription,
  FieldError,
} from "@/shared/components/ui/field";

interface FormPasswordInputProps {
  name: string;
  label?: string;
  description?: string;
  className?: string;
  inputClassName?: string;
  disabled?: boolean;
  placeholder?: string;
}

export default function FormPasswordInput({
  name,
  label,
  description,
  className,
  inputClassName,
  disabled,
  placeholder,
}: FormPasswordInputProps) {
  const { control } = useFormContext();
  const [showPassword, setShowPassword] = useState(false);

  return (
    <Controller
      name={name}
      control={control}
      render={({ field, fieldState }) => (
        <Field data-invalid={fieldState.invalid} className={className}>
          <FieldLabel htmlFor={name}>{label}</FieldLabel>

          <div className="relative">
            <Input
              {...field}
              id={name}
              type={showPassword ? "text" : "password"}
              aria-invalid={fieldState.invalid}
              placeholder={placeholder}
              className={inputClassName}
              disabled={disabled}
            />

            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              className="absolute inset-y-0 right-2 flex items-center text-muted-foreground hover:text-foreground"
              tabIndex={-1}
            >
              {showPassword ? <Eye size={18} /> : <EyeOff size={18} />}
            </button>
          </div>

          {description && <FieldDescription>{description}</FieldDescription>}

          {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
        </Field>
      )}
    />
  );
}
