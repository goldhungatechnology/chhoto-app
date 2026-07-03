import { usePasswordStrength } from "@/shared/hooks";

import { Field } from "@/shared/components/custom/form";
import { PasswordStrengthIndicator } from "@/shared/components/custom/password-strength-indicator";

// ----------------------------------------------------------------------

const INPUT_CLASS =
  "rounded-none border-0 shadow-none border-b border-gray-300 focus-visible:ring-0 focus:border-black";

// ----------------------------------------------------------------------

export default function ResetPasswordFormFields() {
  const passwordStrength = usePasswordStrength({ fieldName: "password" });

  return (
    <>
      <div className="space-y-2">
        <Field.PasswordInput
          name="password"
          label="New password"
          inputClassName={INPUT_CLASS}
        />

        <PasswordStrengthIndicator result={passwordStrength} />
      </div>

      <Field.PasswordInput
        name="confirm_password"
        label="Confirm password"
        inputClassName={INPUT_CLASS}
      />
    </>
  );
}
