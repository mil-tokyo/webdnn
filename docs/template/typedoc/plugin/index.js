const {ReflectionKind} = require("typedoc/dist/lib/models/reflections/abstract");
const {Component, ConverterComponent} = require("typedoc/dist/lib/converter/components");
const {Converter} = require("typedoc/dist/lib/converter/converter");
const {CommentPlugin} = require("typedoc/dist/lib/converter/plugins/CommentPlugin");
const {getRawComment} = require("typedoc/dist/lib/converter/factories/comment");

class WebDNNPlugin extends ConverterComponent {
    // noinspection JSDuplicatedDeclaration
    initialize() {
        // noinspection JSCheckFunctionSignatures
        this.listenTo(this.owner, {
            [Converter.EVENT_BEGIN]: this.onBegin,
            [Converter.EVENT_CREATE_DECLARATION]: this.onDeclaration,
            [Converter.EVENT_RESOLVE_BEGIN]: this.onBeginResolve
        });
    }

    // noinspection JSUnusedLocalSymbols
    onBegin(context) {
        this.moduleRenames = [];
    }

    // noinspection JSUnusedLocalSymbols
    onDeclaration(context, reflection, node) {
        if (reflection.kindOf(ReflectionKind.ExternalModule)) {
            let comment = getRawComment(node);
            let match = /@module\s+([\w\-_/@]+)/.exec(comment);
            if (match) {
                // Look for @preferred
                let preferred = /@preferred/.exec(comment);
                // Set up a list of renames operations to perform when the resolve phase starts
                this.moduleRenames.push({
                    renameTo: match[1],
                    preferred: preferred !== null,
                    reflection: reflection
                });
            }
        }

        CommentPlugin.removeTags(reflection.comment, 'module');
    }

    onBeginResolve(context) {
        let projRefs = context.project.reflections;
        let refsArray = Object.keys(projRefs).reduce((m, k) => {
            m.push(projRefs[k]);
            return m;
        }, []);

        // Process each rename
        this.moduleRenames.forEach(item => {
            let renaming = item.reflection;
            let mergeTarget = refsArray.filter(ref => ref.kind === renaming.kind && ref.name === item.renameTo)[0];

            if (!mergeTarget) {
                renaming.name = item.renameTo;
                return;
            }

            if (!mergeTarget.children) {
                mergeTarget.children = [];
            }

            let childrenOfRenamed = refsArray.filter(ref => ref.parent === renaming);
            childrenOfRenamed.forEach((ref) => {
                ref.parent = mergeTarget;
                mergeTarget.children.push(ref)
            });

            if (item.preferred) {
                let commentTags = renaming.comment.tags.filter(item => item.tagName === 'preferred');
                if (commentTags.length > 0) {
                    renaming.comment.text = commentTags[0].text;
                }

                mergeTarget.comment = renaming.comment;
            }

            if (renaming.children) renaming.children.length = 0;
            CommentPlugin.removeReflection(context.project, renaming);

            // Remove @module and @preferred from the comment, if found.
            CommentPlugin.removeTags(mergeTarget.comment, "module");
            CommentPlugin.removeTags(mergeTarget.comment, 'preferred');
        });
    }
}

Component({name: 'webdnn-plugin'})(WebDNNPlugin);

module.exports = (PluginHost) => {
    // noinspection JSUnresolvedVariable
    PluginHost.owner.converter.addComponent('webdnn-plugin', WebDNNPlugin);
};
