"use client";

import { useEffect } from "react";

import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from "@/shared/components/ui/input-otp";

// ----------------------------------------------------------------------

interface VerifyOtpInputProps {
  value: string[];
  disabled?: boolean;
  hasError?: boolean;
  //
  onChange: (otp: string[]) => void;
  onComplete?: (code: string) => void;
}

// ----------------------------------------------------------------------

export default function VerifyOtpInput({
  value,
  disabled = false,
  hasError = false,
  //
  onChange,
  onComplete,
}: VerifyOtpInputProps) {
  const otpValue = value.join("");

  useEffect(() => {
    if (otpValue.length === 6 && onComplete) {
      onComplete(otpValue);
    }
  }, [otpValue, onComplete]);

  const handleChange = (newValue: string) => {
    const digits = newValue.split("").slice(0, 6);
    const paddedDigits = [...digits, ...Array(6 - digits.length).fill("")];
    onChange(paddedDigits);
  };

  return (
    <div className="flex justify-center">
      <InputOTP
        maxLength={6}
        value={otpValue}
        onChange={handleChange}
        disabled={disabled}
        aria-invalid={hasError}
      >
        <InputOTPGroup className="gap-2 sm:gap-3">
          {[0, 1, 2, 3, 4, 5].map((index) => (
            <InputOTPSlot
              key={index}
              index={index}
              className={`w-12 h-14 sm:w-14 sm:h-16 text-xl sm:text-2xl rounded-lg border-2 transition-all${
                hasError
                  ? "border-red-300 data-[active=true]:ring-red-500/20 aria-invalid:border-red-500"
                  : "border-slate-200 data-[active=true]:border-slate-900 data-[active=true]:ring-slate-900/20"
              } ${
                value[index]
                  ? "border-slate-900 bg-slate-50"
                  : "hover:border-slate-300"
              }`}
            />
          ))}
        </InputOTPGroup>
      </InputOTP>
    </div>
  );
}
