"use client";

import * as React from "react";
import { FormProvider } from "react-hook-form";
import { Zap } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/shared/components/ui/button";
import { Card } from "@/shared/components/ui/card";
import { useCreateLinkForm } from "../../hooks/use-create-link-form";
import { LinkData } from "../../types";
import { CreateLinkSuccess } from "./create-link-success";
import { CreateLinkFormFields } from "./create-link-form-fields";

export function CreateLinkCard() {
  const [createdLink, setCreatedLink] = React.useState<LinkData | null>(null);

  const handleSuccess = (data: LinkData) => {
    setCreatedLink(data);
  };

  const { methods, onSubmit, isSubmitting, resetForm } =
    useCreateLinkForm(handleSuccess);

  const handleCreateAnother = () => {
    setCreatedLink(null);
    resetForm();
  };

  // Render the Success State
  if (createdLink) {
    return (
      <CreateLinkSuccess
        createdLink={createdLink}
        onCreateAnother={handleCreateAnother}
      />
    );
  }

  // Form State
  return (
    <Card className="w-full max-w-xl bg-card border border-border/60 shadow-xl p-8 rounded-4xl">
      <FormProvider {...methods}>
        <form onSubmit={onSubmit} className="flex flex-col gap-6">
          <CreateLinkFormFields />

          {/* CREATE BUTTON */}
          <Button
            type="submit"
            className={cn(
              "w-full rounded-2xl bg-primary py-6 text-base font-semibold text-white shadow-lg shadow-primary/10 transition-all hover:bg-primary-hover hover:scale-[1.01] hover:shadow-primary/20",
              isSubmitting && "opacity-70 pointer-events-none",
            )}
          >
            {isSubmitting ? (
              <div className="flex items-center justify-center gap-2">
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                <span>Creating...</span>
              </div>
            ) : (
              <div className="flex items-center justify-center gap-2">
                <span>Create Short Link</span>
                <Zap className="size-4 fill-white" />
              </div>
            )}
          </Button>

          {/* Disclaimers */}
          <p className="text-[11px] text-center text-muted-foreground">
            By creating a link, you agree to our{" "}
            <a
              href="#"
              className="underline hover:text-primary transition-colors"
            >
              Terms of Service
            </a>{" "}
            and Privacy Policy.
          </p>
        </form>
      </FormProvider>
    </Card>
  );
}
