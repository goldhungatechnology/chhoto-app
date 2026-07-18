import * as React from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/shared/components/ui/dialog";
import { Button } from "@/shared/components/ui/button";
import { Input } from "@/shared/components/ui/input";
import { useUpdateLink } from "../../api/hooks/use-update-link";
import { LinkData } from "../../types";

interface EditTitleModalProps {
  link: LinkData | null;
  isOpen: boolean;
  onClose: () => void;
}

export function EditTitleModal({ link, isOpen, onClose }: EditTitleModalProps) {
  const [title, setTitle] = React.useState("");
  const { updateLinkAsync, isUpdatingLink } = useUpdateLink();

  React.useEffect(() => {
    if (link) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setTitle(link.title || "");
    }
  }, [link]);

  const handleSave = async () => {
    if (!link) return;
    try {
      await updateLinkAsync({ linkUuid: link.uuid, title: title.trim() || null });
      onClose();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="rounded-3xl sm:max-w-md bg-popover border border-border">
        <DialogHeader>
          <DialogTitle className="text-lg font-bold text-foreground">Edit Link Title</DialogTitle>
        </DialogHeader>
        <div className="space-y-4 py-2">
          <div className="space-y-1.5 text-left">
            <label className="text-xs font-semibold text-muted-foreground select-none">
              Link Title
            </label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g., Summer Campaign Launch"
              className="h-11 rounded-xl border-slate-200 bg-white text-slate-900 shadow-none placeholder:text-slate-400 focus-visible:border-slate-400 focus-visible:ring-0"
            />
          </div>
        </div>
        <DialogFooter className="flex gap-2.5 sm:flex-row flex-col-reverse justify-end mt-4">
          <Button variant="outline" className="rounded-xl h-10 px-4" onClick={onClose} disabled={isUpdatingLink}>
            Cancel
          </Button>
          <Button className="rounded-xl h-10 px-5 bg-primary text-white hover:bg-primary-hover" onClick={handleSave} disabled={isUpdatingLink}>
            {isUpdatingLink ? "Saving..." : "Save Changes"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
