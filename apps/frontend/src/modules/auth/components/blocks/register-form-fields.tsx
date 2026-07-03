import { Field } from "@/shared/components/custom/form";

// ----------------------------------------------------------------------

interface RegisterFormFieldsProps {
  showPassword: boolean;
}

// ----------------------------------------------------------------------

export default function RegisterFormFields({
  showPassword,
}: RegisterFormFieldsProps) {
  return (
    <>
      <Field.Input
        name="email"
        type="email"
        label="Email"
        placeholder="Enter email address"
        inputClassName="h-11 rounded-xl border-slate-200 bg-white text-slate-900 shadow-none placeholder:text-slate-400 focus-visible:border-slate-400 focus-visible:ring-0"
      />

      {showPassword && (
        <Field.PasswordInput
          name="password"
          label="Password"
          placeholder="Enter password"
          inputClassName="h-11 rounded-xl border-slate-200 bg-white text-slate-900 shadow-none placeholder:text-slate-400 focus-visible:border-slate-400 focus-visible:ring-0"
        />
      )}
    </>
  );
}
