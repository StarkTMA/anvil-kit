import { Block, BlockCustomComponent, system } from "@minecraft/server";
import { NAMESPACE } from "./constants";

const LIT = `${NAMESPACE}:lit` as any;

function setLit(block: Block, lit: boolean): void {
	for (const part of block.getParts() ?? [block]) {
		part.setPermutation(part.permutation.withState(LIT, lit));
	}
}

const lampSwitch: BlockCustomComponent = {
	onPlayerInteract: ({ block }) => {
		setLit(block, !block.permutation.getState(LIT));
	},
};

system.beforeEvents.startup.subscribe((init) => {
	init.blockComponentRegistry.registerCustomComponent(`${NAMESPACE}:lamp_switch`, lampSwitch);
});
