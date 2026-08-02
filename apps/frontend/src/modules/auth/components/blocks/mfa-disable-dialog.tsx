"use client";

import * as React from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/shared/components/ui/dialog";
import { Button } from "@/shared/components/ui/button";
import { Field } from "@/shared/components/custom/form";
import { FormProvider, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Loader2, ShieldOff } from "lucide-react";

const disableMfaSchema = z.object({
  password: z.string().min(1, "Password is required to confirm"),
});

type DisableMfaSchema = z.infer<typeof disableMfaSchema>;

interface MfaDisableDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirmDisable: (password: string) => Promise<void>;
  isDisabling?: boolean;
}

export function MfaDisableDialog({
  open,
  onOpenChange,
  onConfirmDisable,
  isDisabling = false,
}: MfaDisableDialogProps) {
  const methods = useForm<DisableMfaSchema>({
    resolver: zodResolver(disableMfaSchema),
    defaultValues: { password: "" },
  });

  const onSubmit = async (data: DisableMfaSchema) => {
    await onConfirmDisable(data.password);
    methods.reset();
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md rounded-3xl p-6 bg-white dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800">
        <DialogHeader className="text-left space-y-2">
          <div className="size-11 rounded-2xl bg-rose-500/10 text-rose-600 dark:bg-rose-500/20 dark:text-rose-400 flex items-center justify-center border border-rose-500/20 w-fit">
            <ShieldOff className="size-5" />
          </div>
          <DialogTitle className="text-lg font-bold text-slate-950 dark:text-zinc-50">
            Disable Multi-Factor Authentication
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            Disabling MFA will make your account less secure. Please enter your account password to confirm.
          </DialogDescription>
        </DialogHeader>

        <FormProvider {...methods}>
          <form onSubmit={methods.handleSubmit(onSubmit)} className="space-y-4 pt-2">
            <Field.PasswordInput
              name="password"
              label="Account Password"
              placeholder="Enter your current password"
              inputClassName="h-11 rounded-xl border border-slate-200 bg-white px-3.5 text-slate-900 shadow-none focus-visible:border-slate-400 dark:border-slate-800 dark:bg-zinc-950 dark:text-zinc-50"
            />

            <DialogFooter className="gap-2 pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isDisabling}
                className="rounded-xl h-10 px-4 border-slate-200 dark:border-zinc-800"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="destructive"
                disabled={isDisabling}
                className="rounded-xl h-10 px-4 bg-rose-600 text-white hover:bg-rose-700 flex items-center gap-2"
              >
                {isDisabling ? (
                  <>
                    <Loader2 className="size-4 animate-spin" />
                    <span>Disabling...</span>
                  </>
                ) : (
                  <span>Confirm Disable</span>
                )}
              </Button>
            </DialogFooter>
          </form>
        </FormProvider>
      </DialogContent>
    </Dialog>
  );
}
